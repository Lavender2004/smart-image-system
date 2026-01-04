import os
import json
from typing import List, Optional
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import models, schemas, security, database, utils, ai_service

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sims_user:sims_password@db:3306/image_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Smart Image System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"],    
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="该用户名已被占用")
    
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, username=user.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

def bg_generate_tags(image_id: int, file_path: str, db: Session):
    print(f"[AI] 开始分析图片 ID: {image_id} ...")
    try:
        tags = ai_service.generate_image_tags(file_path)
    except Exception:
        return

    if tags:
        print(f"[AI] 识别成功，标签: {tags}")
        image = db.query(models.Image).filter(models.Image.id == image_id).first()
        if image:
            for tag_name in tags:
                clean_name = tag_name.strip().lower()
                tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
                if not tag:
                    try:
                        tag = models.Tag(name=clean_name)
                        db.add(tag)
                        db.commit()
                        db.refresh(tag)
                    except Exception:
                        db.rollback()
                        tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
                
                if tag and tag not in image.tags:
                    image.tags.append(tag)
            try:
                db.commit()
            except Exception:
                db.rollback()
    else:
        print("[AI] 未生成标签")

@app.post("/api/v1/upload", response_model=schemas.ImageResponse)
def upload_image(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="必须上传图片")

    try:
        image_info = utils.process_image(file)
    except Exception as e:
        raise HTTPException(500, detail=f"处理失败: {str(e)}")

    db_image = models.Image(
        filename=image_info["filename"],
        file_path=image_info["file_path"],
        thumbnail_path=image_info["thumbnail_path"],
        file_size=image_info["file_size"],
        width=image_info["width"],
        height=image_info["height"],
        capture_date=image_info["capture_date"],
        location=image_info.get("location"), 
        owner_id=current_user.id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    background_tasks.add_task(bg_generate_tags, db_image.id, db_image.file_path, db)

    return db_image

@app.post("/api/v1/chat/describe/{image_id}")
async def describe_cloud_image(
    image_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if not image:
        raise HTTPException(404, detail="图片不存在或无权访问")

    if not os.path.exists(image.file_path):
         raise HTTPException(404, detail="服务器磁盘上找不到该文件")

    try:
        description = ai_service.get_image_description(image.file_path)
        return {
            "description": description,
            "image_url": f"/static/{image.filename}" 
        }
    except Exception as e:
        print(f"Cloud Image Describe Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")

@app.get("/api/v1/search/smart", response_model=List[schemas.ImageResponse])
def smart_search(
    query: str,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if not query.strip(): return []

    all_images = db.query(models.Image).filter(models.Image.owner_id == current_user.id).all()
    
    if not all_images:
        return []

    images_payload = []
    for img in all_images:
        tag_names = [t.name for t in img.tags]
        images_payload.append({
            "id": img.id,
            "filename": img.filename,
            "tags": tag_names,
            "category": img.category,
            "location": img.location
        })

    sorted_ids = ai_service.rank_images_by_relevance(query, images_payload)

    if not sorted_ids:
        return []

    result_images = db.query(models.Image).filter(models.Image.id.in_(sorted_ids)).all()
    img_map = {img.id: img for img in result_images}
    
    final_result = []
    for replace_id in sorted_ids:
        if replace_id in img_map:
            final_result.append(img_map[replace_id])
            
    return final_result

@app.get("/api/v1/images", response_model=List[schemas.ImageResponse])
def get_my_images(
    tag: Optional[str] = None,
    sort_by: Optional[str] = Query("date_desc"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Image).filter(models.Image.owner_id == current_user.id)
    if tag:
        query = query.filter(
            (models.Image.tags.any(models.Tag.name.like(f"%{tag}%"))) |
            (models.Image.filename.like(f"%{tag}%")) | 
            (models.Image.location.like(f"%{tag}%")) | 
            (models.Image.category.like(f"%{tag}%"))
        )
    if sort_by == "date_asc": query = query.order_by(models.Image.capture_date.asc())
    elif sort_by == "view_desc": query = query.order_by(models.Image.view_count.desc())
    elif sort_by == "name_asc": query = query.order_by(models.Image.filename.asc())
    else: query = query.order_by(models.Image.capture_date.desc())
    return query.all()

@app.get("/api/v1/images/{image_id}", response_model=schemas.ImageResponse)
def get_image_detail(image_id: int, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image: raise HTTPException(404, detail="Not Found")
    image.view_count += 1
    db.commit()
    db.refresh(image)
    return image

@app.put("/api/v1/images/{image_id}", response_model=schemas.ImageResponse)
def update_image_info(image_id: int, info: schemas.ImageUpdate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if not image: raise HTTPException(404, detail="Not Found")
    if info.filename: image.filename = info.filename
    if info.location: image.location = info.location
    if info.category: image.category = info.category
    if info.capture_date: image.capture_date = info.capture_date
    db.commit()
    db.refresh(image)
    return image

@app.delete("/api/v1/images/{image_id}/tags/{tag_id}")
def delete_tag_from_image(image_id: int, tag_id: int, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if image and tag and tag in image.tags:
        image.tags.remove(tag)
        db.commit()
    return {"msg": "Deleted"}

@app.post("/api/v1/images/{image_id}/tags", response_model=schemas.ImageResponse)
def add_tag_to_image(image_id: int, tag_name: str, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    clean_name = tag_name.strip().lower()
    tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
    if not tag:
        try:
            tag = models.Tag(name=clean_name)
            db.add(tag)
            db.commit()
        except Exception:
            db.rollback()
            tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
            
    if tag and tag not in image.tags:
        image.tags.append(tag)
        db.commit()
        db.refresh(image)
    return image

@app.delete("/api/v1/images/{image_id}", status_code=204)
def delete_image(image_id: int, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if image:
        try:
            if os.path.exists(image.file_path): os.remove(image.file_path)
            if image.thumbnail_path: os.remove(image.thumbnail_path)
        except: pass
        db.delete(image)
        db.commit()
    return None

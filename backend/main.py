import os  # 【新增】用于删除物理文件
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

from . import models, schemas, security, database, utils

# 自动建表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart Image System")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# =======================
# 认证接口
# =======================

@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# =======================
# 图片核心接口
# =======================

@app.post("/api/v1/upload", response_model=schemas.ImageResponse)
def upload_image(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="File must be an image")

    try:
        image_info = utils.process_image(file)
    except Exception as e:
        raise HTTPException(500, detail=f"Image processing failed: {str(e)}")

    db_image = models.Image(
        filename=image_info["filename"],
        file_path=image_info["file_path"],
        thumbnail_path=image_info["thumbnail_path"],
        file_size=image_info["file_size"],
        width=image_info["width"],
        height=image_info["height"],
        owner_id=current_user.id
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

@app.get("/api/v1/images", response_model=List[schemas.ImageResponse])
def get_my_images(
    tag: Optional[str] = Query(None, description="通过标签名筛选"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Image).filter(models.Image.owner_id == current_user.id)
    if tag:
        query = query.filter(models.Image.tags.any(models.Tag.name == tag))
    return query.all()

@app.post("/api/v1/images/{image_id}/tags", response_model=schemas.ImageResponse)
def add_tag_to_image(
    image_id: int,
    tag_name: str,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(
        models.Image.id == image_id, 
        models.Image.owner_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    clean_tag_name = tag_name.strip().lower()
    tag = db.query(models.Tag).filter(models.Tag.name == clean_tag_name).first()
    
    if not tag:
        tag = models.Tag(name=clean_tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    
    if tag not in image.tags:
        image.tags.append(tag)
        db.commit()
        db.refresh(image)
        
    return image

# 【Week 4 新增】删除图片接口
@app.delete("/api/v1/images/{image_id}", status_code=204)
def delete_image(
    image_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. 查数据库，确保是自己的图
    image = db.query(models.Image).filter(
        models.Image.id == image_id,
        models.Image.owner_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # 2. 尝试删除物理文件 (原图 + 缩略图)
    # 使用 try-except 防止因为文件不存在而报错导致数据库删不掉
    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        if image.thumbnail_path and os.path.exists(image.thumbnail_path):
            os.remove(image.thumbnail_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    # 3. 删除数据库记录
    db.delete(image)
    db.commit()
    
    return None

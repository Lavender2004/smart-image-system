import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Request
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

# 1. 标准 CORS 配置 (处理 API 请求)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# 2. 【新增】强制中间件：确保静态文件也能跨域 (解决 Canvas 污染的关键)
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    # 强制添加允许跨域头，防止浏览器拒绝 Canvas 读取图片数据
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# =======================
# 1. 认证接口
# =======================

@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="该用户名已被占用")

    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(
        email=user.email, username=user.username, password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# =======================
# 2. 图片上传
# =======================

@app.post("/api/v1/upload", response_model=schemas.ImageResponse)
def upload_image(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="必须上传图片文件")

    try:
        image_info = utils.process_image(file)
    except Exception as e:
        raise HTTPException(500, detail=f"图片处理失败: {str(e)}")

    db_image = models.Image(
        filename=image_info["filename"],
        file_path=image_info["file_path"],
        thumbnail_path=image_info["thumbnail_path"],
        file_size=image_info["file_size"],
        width=image_info["width"],
        height=image_info["height"],
        capture_date=image_info["capture_date"],
        owner_id=current_user.id
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# =======================
# 3. 图片查询 (支持排序)
# =======================

@app.get("/api/v1/images", response_model=List[schemas.ImageResponse])
def get_my_images(
    tag: Optional[str] = None,
    sort_by: Optional[str] = Query("date_desc", description="排序: date_asc, date_desc, view_desc, name_asc"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Image).filter(models.Image.owner_id == current_user.id)
    
    if tag:
        query = query.filter(
            (models.Image.tags.any(models.Tag.name.like(f"%{tag}%"))) |
            (models.Image.filename.like(f"%{tag}%")) | 
            (models.Image.location.like(f"%{tag}%")) |
            (models.Image.category.like(f"%{tag}%"))
        )
    
    if sort_by == "date_asc":
        query = query.order_by(models.Image.capture_date.asc())
    elif sort_by == "view_desc":
        query = query.order_by(models.Image.view_count.desc())
    elif sort_by == "name_asc":
        query = query.order_by(models.Image.filename.asc())
    else:
        query = query.order_by(models.Image.capture_date.desc())
        
    return query.all()

# =======================
# 4. 图片详情 (浏览量 +1)
# =======================
@app.get("/api/v1/images/{image_id}", response_model=schemas.ImageResponse)
def get_image_detail(
    image_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(404, detail="图片不存在")
    
    image.view_count += 1
    db.commit()
    db.refresh(image)
    return image

# =======================
# 5. 图片修改 (元数据)
# =======================
@app.put("/api/v1/images/{image_id}", response_model=schemas.ImageResponse)
def update_image_info(
    image_id: int,
    info: schemas.ImageUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(
        models.Image.id == image_id, 
        models.Image.owner_id == current_user.id
    ).first()
    if not image:
        raise HTTPException(404, detail="图片不存在")

    if info.filename: image.filename = info.filename
    if info.location: image.location = info.location
    if info.category: image.category = info.category
    if info.capture_date: image.capture_date = info.capture_date
    
    db.commit()
    db.refresh(image)
    return image

# =======================
# 6. 删除标签
# =======================
@app.delete("/api/v1/images/{image_id}/tags/{tag_id}")
def delete_tag_from_image(
    image_id: int,
    tag_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if not image: raise HTTPException(404, "图片不存在")
    
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag: raise HTTPException(404, "标签不存在")
    
    if tag in image.tags:
        image.tags.remove(tag)
        db.commit()
    return {"msg": "标签已移除"}

# =======================
# 7. 贴标签与删除图片
# =======================
@app.post("/api/v1/images/{image_id}/tags", response_model=schemas.ImageResponse)
def add_tag_to_image(
    image_id: int,
    tag_name: str,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if not image: raise HTTPException(404, detail="Image not found")

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

@app.delete("/api/v1/images/{image_id}", status_code=204)
def delete_image(
    image_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == current_user.id).first()
    if not image: raise HTTPException(404, detail="Image not found")

    try:
        if os.path.exists(image.file_path): os.remove(image.file_path)
        if image.thumbnail_path and os.path.exists(image.thumbnail_path): os.remove(image.thumbnail_path)
    except: pass

    db.delete(image)
    db.commit()
    return None

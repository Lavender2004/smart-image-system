from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
# 【修改1】引入 CORS 中间件
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

# 导入我们可以复用的模块
from . import models, schemas, security, database, utils

# 自动建表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart Image System")

# ===============================
# 【修改2】配置 CORS (解决跨域报错)
# ===============================
app.add_middleware(
    CORSMiddleware,
    # 允许的来源列表。为了方便开发，这里允许所有IP ("*")
    # 如果想更安全，可以改成 ["http://localhost:5173", "http://192.168.126.130:5173"]
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# =======================
# 认证接口 (Week 1)
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
# 图片接口 (Week 2 & 3)
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

# 【Week 3 升级】支持通过 tag 搜索图片
@app.get("/api/v1/images", response_model=List[schemas.ImageResponse])
def get_my_images(
    tag: Optional[str] = Query(None, description="通过标签名筛选图片"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. 基础查询：查出属于当前用户的所有图片
    query = db.query(models.Image).filter(models.Image.owner_id == current_user.id)
    
    # 2. 如果用户传了 tag 参数，就加一个筛选条件
    if tag:
        # any() 表示：这张图片的 tags 列表里，有没有任意一个 tag 的名字等于查询词
        query = query.filter(models.Image.tags.any(models.Tag.name == tag))
    
    return query.all()

# =======================
# 标签接口 (Week 3 新增)
# =======================

@app.post("/api/v1/images/{image_id}/tags", response_model=schemas.ImageResponse)
def add_tag_to_image(
    image_id: int,
    tag_name: str,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. 检查图片是否存在，且是否属于当前用户
    image = db.query(models.Image).filter(
        models.Image.id == image_id, 
        models.Image.owner_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # 2. 检查标签是否已存在，不存在则自动创建 (智能处理)
    # 注意：我们用 strip() 去除首尾空格，用 lower() 统一转小写，避免 "Cat" 和 "cat" 重复
    clean_tag_name = tag_name.strip().lower()
    tag = db.query(models.Tag).filter(models.Tag.name == clean_tag_name).first()
    
    if not tag:
        tag = models.Tag(name=clean_tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    
    # 3. 给图片贴标签 (如果还没贴过)
    if tag not in image.tags:
        image.tags.append(tag)
        db.commit()
        db.refresh(image)
        
    return image

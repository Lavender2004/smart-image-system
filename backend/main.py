from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm  # 【修改1】新增导入
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# 导入我们可以复用的模块
from . import models, schemas, security, database, utils

# 自动建表 (如果表不存在)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart Image System")

# 【关键步骤】挂载静态文件目录
# 这样前端就可以通过 http://IP:8000/static/uploads/文件名.jpg 访问图片了
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

# 【修改2】移除了 class LoginRequest，改用 OAuth2 标准表单
@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 【修改3】使用 form_data.username 获取用户名
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # 【修改3】使用 form_data.password 获取密码
    if not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# =======================
# 图片接口 (Week 2 新增)
# =======================

@app.post("/api/v1/upload", response_model=schemas.ImageResponse)
def upload_image(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(security.get_current_user), # 必须登录才能上传
    db: Session = Depends(database.get_db)
):
    # 1. 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="File must be an image")

    # 2. 调用工具箱处理图片 (保存、缩略图)
    try:
        image_info = utils.process_image(file)
    except Exception as e:
        raise HTTPException(500, detail=f"Image processing failed: {str(e)}")

    # 3. 在数据库记录信息
    db_image = models.Image(
        filename=image_info["filename"],
        file_path=image_info["file_path"],
        thumbnail_path=image_info["thumbnail_path"],
        file_size=image_info["file_size"],
        width=image_info["width"],
        height=image_info["height"],
        owner_id=current_user.id  # 绑定给当前登录用户
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

@app.get("/api/v1/images", response_model=List[schemas.ImageResponse])
def get_my_images(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 获取当前用户的所有图片
    return db.query(models.Image).filter(models.Image.owner_id == current_user.id).all()

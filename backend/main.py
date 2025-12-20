from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

# 导入我们需要的所有模块
from . import models, schemas, security, database

# 自动建表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart Image System")

# 注册接口: POST /api/v1/auth/register 
@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. 检查邮箱是否已存在
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. 检查用户名是否已存在
    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # 3. 创建新用户 (密码加密)
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

# 登录接口: POST /api/v1/auth/login 
# 这里的实现为了简单，使用 JSON Body 接收账号密码
class LoginRequest(schemas.BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(login_data: LoginRequest, db: Session = Depends(database.get_db)):
    # 1. 查找用户
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # 2. 验证密码
    if not security.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 3. 生成 Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel, EmailStr

# 注册时的请求体
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 登录后的响应体 (Token)
class Token(BaseModel):
    access_token: str
    token_type: str

# 返回给前端的用户信息 (不包含密码)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

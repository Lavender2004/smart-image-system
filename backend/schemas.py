from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# =======================
# 用户相关模型
# =======================

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


# =======================
# 图片相关模型 (新增)
# =======================

# 图片响应模型
class ImageResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    thumbnail_path: Optional[str] = None
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

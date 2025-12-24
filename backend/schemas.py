from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List  # 新增了 List

# =======================
# 用户相关模型
# =======================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

# =======================
# 标签模型 (Week 3 新增)
# =======================
class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

# =======================
# 图片相关模型
# =======================
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
    
    # 【新增】返回图片时，顺便带上它拥有的标签
    tags: List[TagResponse] = [] 

    class Config:
        from_attributes = True

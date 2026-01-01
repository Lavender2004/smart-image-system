from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, description="用户名至少3位")
    email: EmailStr
    password: str = Field(..., min_length=6, description="密码至少6位")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能小于6位')
        return v

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

class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True

class ImageUpdate(BaseModel):
    filename: Optional[str] = None
    capture_date: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None

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
    
    capture_date: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    view_count: int = 0
    
    tags: List[TagResponse] = [] 

    class Config:
        from_attributes = True

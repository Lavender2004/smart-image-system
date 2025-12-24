from sqlalchemy import Boolean, Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    # 1. 基础字段
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 2. 状态与时间字段
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 3. 存储配额字段 (默认 1GB)
    storage_quota = Column(BigInteger, default=1073741824)
    used_storage = Column(BigInteger, default=0)

    # 4. 【新增】建立与 Image 表的关系
    # 这样我们可以通过 user.images 获取该用户上传的所有图片
    images = relationship("Image", back_populates="owner")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)      # 原始文件名
    file_path = Column(String(255), nullable=False)     # 实际存储路径
    thumbnail_path = Column(String(255), nullable=True) # 缩略图路径
    file_size = Column(Integer, nullable=False)         # 文件大小 (字节)
    
    # 图片元数据 (EXIF信息)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    camera_model = Column(String(100), nullable=True)
    capture_date = Column(TIMESTAMP, nullable=True)
    
    # 外键关联
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 反向关联
    owner = relationship("User", back_populates="images")

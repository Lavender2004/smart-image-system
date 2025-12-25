from sqlalchemy import Boolean, Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey, Table, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

# =======================
# 中间关联表 (保持不变)
# =======================
image_tags = Table(
    'image_tags',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# =======================
# 用户模型 (保持不变)
# =======================
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)

    images = relationship("Image", back_populates="owner")

# =======================
# 标签模型 (保持不变)
# =======================
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    images = relationship("Image", secondary=image_tags, back_populates="tags")

# =======================
# 图片模型 (Week 4.5 重大升级)
# =======================
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=False)
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # 【新增字段】
    # 拍摄时间 (默认为上传时间，后续可通过EXIF提取)
    capture_date = Column(TIMESTAMP, server_default=func.now()) 
    # 拍摄地点 (如: Tokyo, Japan)
    location = Column(String(255), nullable=True)
    # 图片类型 (用户可选: 人像, 风景, 美食, 文字, 其他)
    category = Column(String(50), default="其他")
    # 浏览次数 (用于轮播图排序)
    view_count = Column(Integer, default=0)

    owner_id = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("User", back_populates="images")
    tags = relationship("Tag", secondary=image_tags, back_populates="images")

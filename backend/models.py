from sqlalchemy import Boolean, Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

# =======================
# 中间关联表 (多对多)
# =======================
# 这张表没有对应的类，它只负责连接 images 和 tags
image_tags = Table(
    'image_tags',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# =======================
# 数据模型类
# =======================

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)
    
    storage_quota = Column(BigInteger, default=1073741824)
    used_storage = Column(BigInteger, default=0)

    # 关联关系
    images = relationship("Image", back_populates="owner")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False) # 标签名不能重复

    # 反向关联：通过 tags 可以查到有哪些图片
    images = relationship("Image", secondary=image_tags, back_populates="tags")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=False)
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    camera_model = Column(String(100), nullable=True)
    capture_date = Column(TIMESTAMP, nullable=True)
    
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关联关系
    owner = relationship("User", back_populates="images")
    
    # 【新增】标签关联 (secondary 指向中间表)
    tags = relationship("Tag", secondary=image_tags, back_populates="images")

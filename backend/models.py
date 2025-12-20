from sqlalchemy import Boolean, Column, Integer, String, BigInteger, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    # 根据设计文档定义字段
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 时间和状态
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 存储空间 (默认1GB)
    storage_quota = Column(BigInteger, default=1073741824)
    used_storage = Column(BigInteger, default=0)

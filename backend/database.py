from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 连接到 Docker 中的 MySQL
# 用户名: sims_user, 密码: sims_password, 端口: 3306, 库名: image_db
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sims_user:sims_password@localhost:3306/image_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

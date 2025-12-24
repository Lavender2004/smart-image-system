import os
import shutil
import uuid
from PIL import Image
from fastapi import UploadFile

# 定义存储路径 (和 docker-compose 里的卷对应)
UPLOAD_DIR = "static/uploads"
THUMBNAIL_DIR = "static/thumbnails"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def process_image(file: UploadFile):
    """
    图片处理流水线:
    1. 生成唯一文件名 (防止重名覆盖)
    2. 保存原图
    3. 生成缩略图
    4. 提取基础元数据
    """
    # 1. 生成唯一文件名 (UUID + 原扩展名)
    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    thumb_path = os.path.join(THUMBNAIL_DIR, unique_filename)

    # 2. 保存原图
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 3. 使用 Pillow 处理图片
    with Image.open(file_path) as img:
        # 获取元数据
        width, height = img.size
        
        # 生成缩略图 (最大 200x200)
        img.thumbnail((200, 200))
        img.save(thumb_path)

    # 4. 获取文件大小
    file_size = os.path.getsize(file_path)

    return {
        "filename": unique_filename,
        "file_path": file_path,
        "thumbnail_path": thumb_path,
        "file_size": file_size,
        "width": width,
        "height": height
    }

import os
import shutil
from datetime import datetime
from PIL import Image, ExifTags
from fastapi import UploadFile

# 定义常量
UPLOAD_DIR = "static/uploads"
THUMBNAIL_DIR = "static/thumbnails"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def get_exif_data(pil_image):
    """尝试从图片提取拍摄时间"""
    capture_date = None
    try:
        # 获取图片的 EXIF 原始数据
        info = pil_image._getexif()
        if info:
            for tag, value in info.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                # 36867 是 DateTimeOriginal (拍摄时间)
                if decoded == "DateTimeOriginal":
                    try:
                        # EXIF 时间格式通常是 "YYYY:MM:DD HH:MM:SS"
                        capture_date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        break
                    except:
                        pass
    except Exception as e:
        print(f"EXIF read error: {e}")
        
    return capture_date

def process_image(file: UploadFile):
    """保存原图、生成缩略图、提取元数据"""
    
    # 1. 生成唯一文件名
    import uuid
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, unique_filename)

    # 2. 保存原图到硬盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. 使用 Pillow 处理图片
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            
            # 【新增】尝试读取 EXIF 拍摄时间
            # 如果读不到，就用当前时间
            capture_time = get_exif_data(img) or datetime.now()

            # 生成缩略图
            img.thumbnail((400, 400))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumbnail_path, "JPEG")
            
            return {
                "filename": file.filename,
                "file_path": file_path,
                "thumbnail_path": thumbnail_path,
                "file_size": os.path.getsize(file_path),
                "width": width,
                "height": height,
                "capture_date": capture_time # 返回时间
            }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

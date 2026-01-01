import os
import shutil
import uuid
from datetime import datetime
from PIL import Image, ExifTags, ImageOps
from fastapi import UploadFile
from geopy.geocoders import Nominatim

UPLOAD_DIR = "static/uploads"
THUMBNAIL_DIR = "static/thumbnails"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

geolocator = Nominatim(user_agent="zju_image_system_student_demo")

def _convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    if not exif_data: return None

    gps_info_tag = next((k for k, v in ExifTags.TAGS.items() if v == "GPSInfo"), None)
    gps_info = exif_data.get(gps_info_tag)
    
    if not gps_info: return None

    lat = gps_info.get(2)
    lat_ref = gps_info.get(1)
    lon = gps_info.get(4)
    lon_ref = gps_info.get(3)

    if lat and lat_ref and lon and lon_ref:
        try:
            lat = _convert_to_degrees(lat)
            if lat_ref != "N": lat = -lat
            lon = _convert_to_degrees(lon)
            if lon_ref != "E": lon = -lon
            return lat, lon
        except:
            return None
    return None

def get_location_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='zh-cn', timeout=10)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('county')
            state = address.get('state')
            parts = [p for p in [state, city] if p]
            return " ".join(dict.fromkeys(parts)) 
    except:
        pass
    return None

def get_exif_data(pil_image):
    capture_date = None
    location_str = None

    try:
        exif_raw = pil_image._getexif()
        if exif_raw:
            for tag, value in exif_raw.items():
                if ExifTags.TAGS.get(tag) == "DateTimeOriginal":
                    try:
                        capture_date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    except: pass
            
            lat_lon = get_lat_lon(exif_raw)
            if lat_lon:
                location_str = get_location_name(lat_lon[0], lat_lon[1])
                
    except Exception as e:
        print(f"EXIF error: {e}")
    
    return capture_date, location_str

def process_image(file: UploadFile):
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)
            width, height = img.size
            
            capture_time, location_name = get_exif_data(img)
            
            img.thumbnail((400, 400))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(thumbnail_path, "JPEG")
            
            return {
                "filename": file.filename,
                "file_path": file_path,
                "thumbnail_path": thumbnail_path,
                "file_size": os.path.getsize(file_path),
                "width": width,
                "height": height,
                "capture_date": capture_time or datetime.now(),
                "location": location_name
            }
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise e

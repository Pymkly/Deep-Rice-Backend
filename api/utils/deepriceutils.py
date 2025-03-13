import json
import os
import time
from typing import List
from fastapi import UploadFile, File

## Variables
with open("pass.json") as config_file:
    _secret_key = json.load(config_file)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Fonctions
def allowed_images(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension_category(extension):
    extension_map = {
        "pdf": "pdf",
        "csv": "csv",
        "jpg": "image",
        "jpeg": "image",
        "png": "image",
        "bmp": "image",
        "tiff": "image",
        "docx": "word",
        "doc": "word",
    }
    return extension_map.get(extension.lower(), "autres")  # Par défaut "autres"

def get_file_extension(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    ext = ext.split(".")[-1]
    return ext

def vector_to_str(vector):
    return "[" + ",".join(map(str, vector)) + "]"

def huggingface_api_token():
    return _secret_key.get("HUGGINGFACEHUB_API_TOKEN")

def get_files(folder, extension):
    return [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(extension)]

def get_files_on_folder(folder, extension):
    sub_folder = get_file_extension_category(extension)
    path_ = str(os.path.join(folder, sub_folder))
    if not (os.path.exists(path_) and os.path.isdir(path_)):
        os.makedirs(path_)
        return []
    return [os.path.join(path_, file) for file in os.listdir(path_)]

def get_csv_files(folder):
    return get_files(folder, ".csv")

def get_pdf_files(directory):
    return get_files(directory, ".pdf")

def readable_polygone(boundary_wkt):
    if boundary_wkt.startswith("POLYGON"):
        polygon_coords = boundary_wkt.replace("POLYGON((", "").replace("))", "").split(",")
        print(polygon_coords)
        return [
            tuple(map(float, coord.split(" "))) for coord in polygon_coords
        ]
    return None

def readable_point(location_wkt):
    if location_wkt.startswith("POINT"):
        point_coords = location_wkt.replace("POINT(", "").replace(")", "").split()
        latitude, longitude = map(float, point_coords)
        return latitude, longitude
    return None, None

async def upload_images(files: List[UploadFile] = File(...)):
    image_names = []
    for file in files:
        # Sauvegarder chaque image
        unique_filename = f"{int(time.time())}_{file.filename}"
        file_location = f"uploads/{unique_filename}"
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        image_names.append(file_location)
    return image_names
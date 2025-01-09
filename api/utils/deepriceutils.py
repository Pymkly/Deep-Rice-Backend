import time
from typing import List
from fastapi import UploadFile, File

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
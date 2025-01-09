import time
from typing import List

from fastapi import FastAPI, UploadFile, File
import uvicorn

from api.lands.lands import get_land_data
from api.predict import predict_disease_on_images
from api.sensors.drone.dronecontroller import upload_drone_image
from api.sensors.drone.dronereport import get_all_report_without_con, get_drone_report_with_details_without_con

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/drone-reports")
async def get_all_report_end_point():
    return await get_all_report_without_con()

@app.get("/drone-report/{report_id}")
def get_land_endpoint(report_id: int):
    return get_drone_report_with_details_without_con(report_id)

@app.get("/land/{land_id}")
def get_land_endpoint(land_id: int):
    return get_land_data(land_id)


@app.post("/upload-drone-image/")
async def upload_drone_image_end_point(files: List[UploadFile] = File(...)):
    return await upload_drone_image(files)

@app.post("/predict-disease/")
async def predict_disease_end_point(files: List[UploadFile] = File(...)):
    return await predict_disease_on_images(files)

@app.post("/upload-images/")
async def upload_images(files: List[UploadFile] = File(...)):
    image_names = []
    for file in files:
        # Sauvegarder chaque image
        unique_filename = f"{int(time.time())}_{file.filename}"
        file_location = f"uploads/{unique_filename}"
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        image_names.append(file.filename)
    return {"message": "Images uploaded successfully", "uploaded_files": image_names}

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0",
                port=8000, reload=True)
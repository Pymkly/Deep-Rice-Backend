from typing import List

from fastapi import APIRouter, UploadFile, File

from api.database.conn import get_conn
from api.predict import predict_disease_on_images

router = APIRouter()

conn = get_conn()

@router.post("/disease-detection/images")
async def predict_disease(files: List[UploadFile] = File(...)):
    cursor = conn.cursor()
    result = await predict_disease_on_images(files_=files, cursor=cursor)
    cursor.close()
    return result
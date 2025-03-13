from typing import List

from fastapi import APIRouter, UploadFile, File

from api.database.conn import get_conn
from api.sensors.drone.dronecontroller import upload_drone_image
from api.sensors.drone.dronereport import get_all_report, drone_report_one

router = APIRouter()

conn = get_conn()

@router.get("/drone-reports")
async def get_reports():
    cursor = conn.cursor()
    result = get_all_report(cursor)
    cursor.close()
    return result

@router.get("/drone-reports/{report_id}")
def get_drone_report(report_id: int):
    cursor = conn.cursor()
    result = drone_report_one(report_id, cursor)
    cursor.close()
    return result

@router.post("/drone-reports/images/upload")
async def upload_drone_image_end_point(files: List[UploadFile] = File(...)):
    return await upload_drone_image(files)
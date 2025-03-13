from fastapi import APIRouter

from api.database.conn import get_conn
from api.lands.lands import get_land_data_with_cursor

router = APIRouter()

conn = get_conn()

@router.get("/land/{land_id}")
def get_land_endpoint(land_id: int):
    cursor = conn.cursor()
    result = get_land_data_with_cursor(land_id, cursor)
    cursor.close()
    return result


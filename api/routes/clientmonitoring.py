from fastapi import APIRouter

from api.database.conn import get_conn
from api.monitoring.poto import get_potos

router = APIRouter()

conn = get_conn()

@router.get("/monitoring/{land_id}")
async def refresh_rag(land_id: int):
    cursor = conn.cursor()
    result = get_potos(land_id, cursor)
    cursor.close()
    return result

from fastapi import APIRouter

from api.database.conn import get_conn
from api.ragsystem.rice.agent.agent import RiceAgent

router = APIRouter()

agent = RiceAgent()
conn = get_conn()

@router.get("/reload")
async def save_documents():
    agent.save_documents()
    return {"message": "ok"}
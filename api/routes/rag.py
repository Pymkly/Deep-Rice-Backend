from fastapi import APIRouter
from pydantic import BaseModel

from api.database.conn import get_conn
from api.ragsystem.rice.agent.agent import RiceAgent

router = APIRouter()

agent = RiceAgent()
conn = get_conn()

class QueryModel(BaseModel):
    query: str

@router.get("/rag/refresh")
async def refresh_rag():
    agent.refresh()
    return {"message": "Done"}

@router.post("/rag/query/")
async def query_rag(request: QueryModel):
    cur = conn.cursor()
    user_response, _prompt = agent.ask(request.query, cur)
    cur.close()
    response_ = {
        'user_response': user_response,
        'prompt': _prompt,
    }
    return response_


import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from api.routes.drone import router as drone_router
from api.routes.land import router as land_router
from api.routes.rag import router as rag_router
from api.routes.upload import router as upload_router
from api.routes.disease import router as disease_router
from api.routes.restricted import router as restricted_router

app = FastAPI()

app.include_router(rag_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(drone_router, prefix="/api")
app.include_router(land_router, prefix="/api")  
app.include_router(disease_router, prefix="/api")
app.include_router(restricted_router, prefix="/su")

class QueryModel(BaseModel):
    query: str
@app.get("/ping")
async def ping():
    return {"message": "pong"}


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0",
                port=8000, reload=True)
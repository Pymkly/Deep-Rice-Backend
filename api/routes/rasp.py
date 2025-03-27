from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import  Dict
import logging
from datetime import datetime
from api.database.conn import get_mongo_db
from api.routes.monitoring import update_client_data

# from api.database.conn import get_conn

router = APIRouter()

client, db = get_mongo_db()
# conn = get_conn()

class SensorData(BaseModel):
    type: str
    ref: str
    data: Dict[str, float]

@router.post("/sensor-data")
async def sensor_data_handler(_sensor_data: SensorData):
    """
       Cette route reçoit les données et les stocke dans MongoDB.
    """
    try:
        print(_sensor_data)
        data_to_insert = _sensor_data.dict()
        data_to_insert["timestamp"] = datetime.now().isoformat()
        collection = data_to_insert["type"]
        logging.info("data received" + str(data_to_insert))
        sensor_collection = db[collection]
        sensor_collection.insert_one(data_to_insert)
        await update_client_data()
        return {"message": "✅ Données stockées avec succès"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement dans MongoDB : {str(e)}")



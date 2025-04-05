from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from api.monitoring.monitoring_manager import MonitoringManager

# import asyncio
# from api.database.conn import get_mongo_db

router = APIRouter()
monitoring_manager = MonitoringManager()
# client, db = get_mongo_db()

active_connections = []

fake_sensor_data = [
    {
        "DHT22": {"Humidity": "30%", "Temperature": "6°C"},
        "NPK": {"N": "100", "P": "45", "K": "55"}
    },
    {
        "DHT22": {"Humidity": "40%", "Temperature": "10°C"},
        "NPK": {"N": "50", "P": "30", "K": "22"}
    }
]
t = 0
import json
@router.websocket("/monitoring")
async def web_socket(_websocket: WebSocket):
    await _websocket.accept()
    active_connections.append(_websocket)

    try:
        while True:
            # Garde la connexion active
            await _websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(_websocket)
        print("Client déconnecté.")



async def update_client_data():
    global t
    print("updated")
    data = monitoring_manager.collect_last(1)
    print(data)

    for _websocket in active_connections:
        await _websocket.send_text(json.dumps(data))
        # t = 1 if t == 0 else 0


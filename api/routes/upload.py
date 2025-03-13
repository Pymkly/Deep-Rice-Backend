import os
import time
from fastapi import APIRouter, UploadFile, File
from typing import List

from api.database.conn import get_conn
from api.ragsystem.rice.agent.agent import RiceAgent

router = APIRouter()

agent = RiceAgent()
conn = get_conn()

@router.post("/rag/upload")
async def upload_file(file: UploadFile = File(...)):
    # Sauvegarder le fichier
    temp_base_path =  "./uploads/"
    os.makedirs(temp_base_path, exist_ok=True)
    file_path = os.path.join(temp_base_path, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())  # Lire tout le contenu et l'écrire
    try:
        cur = conn.cursor()
        agent.process_file(cur, file_path)
        cur.close()
        return {"message": "done"}, 200
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500

@router.post("/drone/images")
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


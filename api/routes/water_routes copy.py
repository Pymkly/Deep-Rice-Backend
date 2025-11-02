from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
import sys
sys.path.append('..') 
from api.water.water_model import *
from api.water.water_prediction import WaterPredictor

router = APIRouter(
    prefix="/water",
    tags=["Water Management"]
)

@router.get("/")
def get_water_status():
    return {"message": "Water route OK"}

# Instance du prédicteur (chargé une seule fois)
predictor = WaterPredictor(model_path="water_model.h5")

@router.post("/predict", response_model=WaterPredictionResponse)
async def predict_water_needs(request: WaterPredictionRequest):
    """
    Prédit les besoins en eau pour les 7 prochains jours
    
    - **field_id**: ID du champ de riz
    - **weather_forecast**: Prévisions météo 7 jours
    - **current_soil_moisture**: Humidité actuelle du sol (optionnel)
    """
    try:
        predictions = predictor.predict(
            field_id=request.field_id,
            weather_data=request.weather_forecast,
            soil_moisture=request.current_soil_moisture
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {str(e)}")

@router.get("/recommendations/{field_id}", response_model=List[IrrigationRecommendation])
async def get_irrigation_recommendations(
    field_id: str,
    days: int = Query(default=7, ge=1, le=14, description="Nombre de jours")
):
    """
    Génère des recommandations d'irrigation pour un champ
    
    - **field_id**: ID du champ
    - **days**: Nombre de jours de recommandations (1-14)
    """
    try:
        recommendations = predictor.generate_recommendations(field_id, days)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Champ non trouvé: {str(e)}")

@router.get("/alerts/{field_id}", response_model=List[WaterAlert])
async def get_water_alerts(field_id: str):
    """
    Récupère les alertes hydriques actives pour un champ
    
    - **field_id**: ID du champ
    """
    try:
        alerts = predictor.get_active_alerts(field_id)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/{field_id}", response_model=WaterStatistics)
async def get_water_statistics(
    field_id: str,
    start_date: datetime = Query(..., description="Date de début"),
    end_date: datetime = Query(..., description="Date de fin")
):
    """
    Statistiques de consommation d'eau sur une période
    
    - **field_id**: ID du champ
    - **start_date**: Date de début de la période
    - **end_date**: Date de fin de la période
    """
    try:
        stats = predictor.calculate_statistics(field_id, start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sensor-data", status_code=201)
async def record_sensor_data(data: SoilMoistureData):
    """
    Enregistre les données d'un capteur d'humidité du sol
    
    - **data**: Données du capteur IoT
    """
    try:
        # TODO: Sauvegarder dans la base de données
        return {"status": "success", "message": "Données capteur enregistrées"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fields", response_model=List[FieldData])
async def list_fields():
    """
    Liste tous les champs de riz enregistrés
    """
    try:
        # TODO: Récupérer depuis la base de données
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fields", response_model=FieldData, status_code=201)
async def create_field(field: FieldData):
    """
    Crée un nouveau champ de riz dans le système
    
    - **field**: Données du champ
    """
    try:
        # TODO: Sauvegarder dans la base de données
        return field
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime, timedelta

from api.water.water_model import *
from api.water.water_prediction import WaterPredictor

from api.water.water_database import (
create_field,
get_all_fields,
get_field_by_id,
save_sensor_data,
save_prediction,
get_active_alerts as db_get_active_alerts,
calculate_and_cache_statistics,
create_alert
)

router = APIRouter(
    prefix="/water",
    tags=["Water Management"]
)
  
@router.get("/")
def get_water_status():
    return {
        "message": "Water Management Module",
        "status": "operational",
        "version": "1.0.0"
    }

# Instance du prédicteur (chargé une seule fois)
predictor = WaterPredictor(model_path="api/ml/water_model.keras")

# ============================================================================
# ENDPOINTS PRÉDICTIONS
# ============================================================================

@router.post("/predict", response_model=WaterPredictionResponse)
async def predict_water_needs(request: WaterPredictionRequest):
    """
    Prédit les besoins en eau pour les 7 prochains jours
    
    - **field_id**: ID du champ de riz
    - **weather_forecast**: Prévisions météo 7 jours
    - **current_soil_moisture**: Humidité actuelle du sol (optionnel)
    """
    try:
        # Vérifier que le champ existe
        field = get_field_by_id(request.field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {request.field_id} non trouvé")
        
        # Faire la prédiction
        predictions = predictor.predict(
            field_id=request.field_id,
            weather_data=request.weather_forecast,
            soil_moisture=request.current_soil_moisture
        )
        
        # Sauvegarder dans la base de données
        try:
            save_prediction(
                field_id=request.field_id,
                prediction_date=predictions.prediction_date,
                daily_predictions=predictions.daily_predictions,
                model_version="v1.0"
            )
        except Exception as db_error:
            print(f"⚠️ Erreur sauvegarde prédiction: {db_error}")
            # On continue même si la sauvegarde échoue
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {str(e)}")

# ============================================================================
# ENDPOINTS RECOMMANDATIONS
# ============================================================================

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
        # Vérifier que le champ existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {field_id} non trouvé")
        
        recommendations = predictor.generate_recommendations(field_id, days)
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération recommandations: {str(e)}")

# ============================================================================
# ENDPOINTS ALERTES
# ============================================================================

@router.get("/alerts/{field_id}", response_model=List[WaterAlert])
async def get_water_alerts(field_id: str):
    """
    Récupère les alertes hydriques actives pour un champ
    
    - **field_id**: ID du champ
    """
    try:
        # Vérifier que le champ existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {field_id} non trouvé")
        
        # Récupérer les alertes depuis la DB
        alerts_db = db_get_active_alerts(field_id)
        
        # Convertir en modèles Pydantic
        alerts = []
        for alert_data in alerts_db:
            alert = WaterAlert(
                alert_id=alert_data['alert_id'],
                field_id=alert_data['field_id'],
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                message=alert_data['message'],
                timestamp=alert_data['timestamp'],
                action_required=alert_data.get('action_required')
            )
            alerts.append(alert)
        
        # Si pas d'alertes en DB, générer de nouvelles alertes potentielles
        if not alerts:
            new_alerts = predictor.get_active_alerts(field_id)
            
            # Sauvegarder les nouvelles alertes en DB
            for alert in new_alerts:
                try:
                    create_alert(alert)
                except Exception as e:
                    print(f"⚠️ Erreur sauvegarde alerte: {e}")
            
            return new_alerts
        
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS STATISTIQUES
# ============================================================================

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
        # Vérifier que le champ existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {field_id} non trouvé")
        
        # Calculer et récupérer les statistiques depuis la DB
        stats = calculate_and_cache_statistics(field_id, start_date, end_date)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS CAPTEURS
# ============================================================================

@router.post("/sensor-data", status_code=201)
async def record_sensor_data(data: SoilMoistureData):
    """
    Enregistre les données d'un capteur d'humidité du sol
    
    - **data**: Données du capteur IoT
    """
    try:
        # Vérifier que le champ existe
        field = get_field_by_id(data.field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {data.field_id} non trouvé")
        
        # Sauvegarder dans la base de données
        sensor_data_id = save_sensor_data(data)
        
        return {
            "status": "success",
            "message": "Données capteur enregistrées",
            "sensor_data_id": sensor_data_id,
            "timestamp": data.timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur enregistrement: {str(e)}")

# ============================================================================
# ENDPOINTS CHAMPS
# ============================================================================

@router.get("/fields", response_model=List[dict])
async def list_fields():
    """
    Liste tous les champs de riz enregistrés
    """
    try:
        fields = get_all_fields()
        return fields
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération champs: {str(e)}")

@router.get("/fields/{field_id}")
async def get_field(field_id: str):
    """
    Récupère un champ spécifique par son ID
    
    - **field_id**: ID du champ
    """
    try:
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {field_id} non trouvé")
        return field
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fields", response_model=FieldData, status_code=201)
async def create_new_field(field: FieldData):
    """
    Crée un nouveau champ de riz dans le système
    
    - **field**: Données du champ
    """
    try:
        # Sauvegarder dans la base de données
        created_field = create_field(field)
        return created_field
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création champ: {str(e)}")

@router.delete("/fields/{field_id}", status_code=204)
async def delete_field(field_id: str):
    """
    Désactive un champ (soft delete)
    
    - **field_id**: ID du champ à désactiver
    """
    try:
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail=f"Champ {field_id} non trouvé")
        
        # TODO: Implémenter la désactivation dans water_database.py
        # deactivate_field(field_id)
        
        return {"message": f"Champ {field_id} désactivé"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS MONITORING
# ============================================================================

@router.get("/health")
async def health_check():
    """Vérifie la santé du module water"""
    try:
        from api.water.water_database import check_database_connection
        
        db_status = check_database_connection()
        model_loaded = predictor.model is not None
        
        return {
            "status": "healthy" if (db_status and model_loaded) else "degraded",
            "database": "connected" if db_status else "disconnected",
            "model": "loaded" if model_loaded else "not_loaded",
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }
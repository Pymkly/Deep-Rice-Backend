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
    get_predictions_by_field,
    get_sensor_data_by_field,
    get_active_alerts as db_get_active_alerts,
    calculate_and_cache_statistics,
    create_alert,
    check_database_connection
)

router = APIRouter( 
    tags=["Water Management"]
)

@router.get("/")
def get_water_status():
    """Status du module Water Management"""
    return {
        "message": "Water Management Module",
        "status": "operational",
        "version": "2.0.0",
        "features": "Integrated with parcels/potos structure"
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
    
    - **field_id**: ID de la parcelle (parcel_id)
    - **weather_forecast**: Prévisions météo 7 jours
    - **current_soil_moisture**: Humidité actuelle du sol (optionnel)
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(request.field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {request.field_id} non trouvée"
            )
        
        # Récupérer le stade de croissance (si config existe)
        growth_stage = field.get('crop_type')  # Temporaire, à adapter
        
        # Faire la prédiction
        predictions = predictor.predict(
            field_id=request.field_id,
            weather_data=request.weather_forecast,
            soil_moisture=request.current_soil_moisture,
            growth_stage=growth_stage
        )
        
        # Sauvegarder dans la base de données
        try:
            save_prediction(
                field_id=request.field_id,
                prediction_date=predictions.prediction_date,
                daily_predictions=predictions.daily_predictions,
                model_version="v2.0"
            )
            print(f"✅ Prédictions sauvegardées pour parcelle {request.field_id}")
        except Exception as db_error:
            print(f"⚠️ Erreur sauvegarde prédiction: {db_error}")
            # On continue même si la sauvegarde échoue
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {str(e)}")

@router.get("/predictions/{field_id}")
async def get_field_predictions(field_id: str):
    """
    Récupère toutes les prédictions d'une parcelle
    
    - **field_id**: ID de la parcelle
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # Récupérer les prédictions depuis la DB
        predictions = get_predictions_by_field(field_id)
        
        if not predictions:
            return []  # Retourne liste vide si pas de prédictions
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur récupération prédictions: {str(e)}"
        )

# ============================================================================
# ENDPOINTS RECOMMANDATIONS
# ============================================================================

@router.get("/recommendations/{field_id}", response_model=List[IrrigationRecommendation])
async def get_irrigation_recommendations(
    field_id: str,
    days: int = Query(default=7, ge=1, le=14, description="Nombre de jours")
):
    """
    Génère des recommandations d'irrigation pour une parcelle
    
    - **field_id**: ID de la parcelle
    - **days**: Nombre de jours de recommandations (1-14)
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # Récupérer l'humidité du sol actuelle
        from api.water.water_database import get_average_soil_moisture
        soil_moisture = get_average_soil_moisture(field_id, hours=24)
        
        # Récupérer le stade de croissance
        growth_stage = field.get('crop_type')
        
        # Générer recommandations
        recommendations = predictor.generate_recommendations(
            field_id, 
            days,
            soil_moisture=soil_moisture,
            growth_stage=growth_stage
        )
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur génération recommandations: {str(e)}"
        )

# ============================================================================
# ENDPOINTS ALERTES
# ============================================================================

@router.get("/alerts/{field_id}", response_model=List[WaterAlert])
async def get_water_alerts(field_id: str):
    """
    Récupère les alertes hydriques actives pour une parcelle
    
    - **field_id**: ID de la parcelle
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # Récupérer les alertes depuis la DB
        alerts_db = db_get_active_alerts(field_id)
        
        # Convertir en modèles Pydantic
        alerts = []
        for alert_data in alerts_db:
            alert = WaterAlert(
                alert_id=alert_data['alert_id'],
                field_id=str(alert_data.get('parcel_id', field_id)),
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                message=alert_data['message'],
                timestamp=alert_data['timestamp'],
                action_required=alert_data.get('action_required'),
                is_resolved=alert_data.get('is_resolved', False)
            )
            alerts.append(alert)
        
        # Si pas d'alertes en DB, générer de nouvelles alertes potentielles
        if not alerts:
            # Récupérer humidité sol + dernière lecture capteur
            from api.water.water_database import (
                get_average_soil_moisture,
                get_latest_sensor_data_by_parcel
            )
            
            parcel_id = int(field_id) if field_id.isdigit() else None
            soil_moisture = get_average_soil_moisture(field_id, hours=24) if parcel_id else None
            
            # Dernière lecture capteur
            last_reading = None
            if parcel_id:
                sensor_data = get_latest_sensor_data_by_parcel(parcel_id, limit=1)
                if sensor_data:
                    last_reading = sensor_data[0].get('timestamp')
            
            new_alerts = predictor.get_active_alerts(
                field_id, 
                soil_moisture=soil_moisture,
                last_sensor_reading=last_reading
            )
            
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
    start_date: datetime = Query(..., description="Date de début (YYYY-MM-DD)"),
    end_date: datetime = Query(..., description="Date de fin (YYYY-MM-DD)")
):
    """
    Statistiques de consommation d'eau sur une période
    
    - **field_id**: ID de la parcelle
    - **start_date**: Date de début de la période
    - **end_date**: Date de fin de la période
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # Calculer et récupérer les statistiques depuis la DB
        stats = calculate_and_cache_statistics(field_id, start_date, end_date)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS CAPTEURS (POTOs)
# ============================================================================

@router.post("/sensor-data", status_code=201)
async def record_sensor_data(data: SoilMoistureData):
    """
    Enregistre les données d'un capteur d'humidité du sol
    
    - **poto_id**: ID du POTO où le capteur est installé
    - **data**: Données du capteur IoT
    """
    try:
        # Vérifier que le POTO existe
        # TODO: Ajouter vérification get_poto_by_id
        
        # Sauvegarder dans la base de données
        sensor_data_id = save_sensor_data(data)
        
        return {
            "status": "success",
            "message": "Données capteur enregistrées",
            "sensor_data_id": sensor_data_id,
            "poto_id": data.poto_id,
            "timestamp": data.timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur enregistrement: {str(e)}"
        )

@router.get("/sensor-data/{field_id}")
async def get_field_sensor_data(
    field_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Nombre de lectures")
):
    """
    Récupère les données capteur d'une parcelle
    
    - **field_id**: ID de la parcelle
    - **limit**: Nombre max de lectures à retourner
    """
    try:
        # Vérifier que la parcelle existe
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # Récupérer données capteurs
        sensor_data = get_sensor_data_by_field(field_id, limit)
        
        return sensor_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur récupération données capteur: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARCELLES (FIELDS)
# ============================================================================

@router.get("/fields", response_model=List[dict])
async def list_fields():
    """
    Liste toutes les parcelles avec configuration water
    """
    try:
        fields = get_all_fields()
        return fields
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur récupération parcelles: {str(e)}"
        )

@router.get("/fields/{field_id}")
async def get_field(field_id: str):
    """
    Récupère une parcelle spécifique par son ID
    
    - **field_id**: ID de la parcelle
    """
    try:
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        return field
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fields", response_model=FieldData, status_code=201)
async def create_new_field(field: FieldData):
    """
    Crée une configuration water pour une parcelle
    
    - **field**: Données de la parcelle
    """
    try:
        # Sauvegarder dans la base de données
        created_field = create_field(field)
        return created_field
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur création parcelle: {str(e)}"
        )

@router.put("/fields/{field_id}")
async def update_field(field_id: str, field: FieldData):
    """
    Met à jour une configuration water d'une parcelle
    
    - **field_id**: ID de la parcelle
    - **field**: Nouvelles données
    """
    try:
        existing_field = get_field_by_id(field_id)
        if not existing_field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # TODO: Implémenter update_field dans water_database.py
        # updated_field = update_field_in_db(field_id, field)
        
        return {"message": f"Parcelle {field_id} mise à jour", "field": field}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur mise à jour: {str(e)}"
        )

@router.delete("/fields/{field_id}", status_code=204)
async def delete_field(field_id: str):
    """
    Désactive une configuration water (soft delete)
    
    - **field_id**: ID de la parcelle à désactiver
    """
    try:
        field = get_field_by_id(field_id)
        if not field:
            raise HTTPException(
                status_code=404, 
                detail=f"Parcelle {field_id} non trouvée"
            )
        
        # TODO: Implémenter désactivation dans water_database.py
        # deactivate_field(field_id)
        
        return {"message": f"Configuration water parcelle {field_id} désactivée"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS MONITORING
# ============================================================================

@router.get("/ping")
async def water_ping():
    """Health check rapide du module water"""
    return {
        "status": "ok", 
        "message": "Water module operational",
        "timestamp": datetime.now(),
        "version": "2.0.0"
    }

@router.get("/health")
async def health_check():
    """Vérifie la santé complète du module water"""
    try:
        db_status = check_database_connection()
        model_loaded = predictor.model is not None
        
        return {
            "status": "healthy" if (db_status and model_loaded) else "degraded",
            "database": "connected" if db_status else "disconnected",
            "model": "loaded" if model_loaded else "not_loaded",
            "model_path": "api/ml/water_model.keras",
            "features_count": 7,  # 7 features (sans solar_radiation)
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }
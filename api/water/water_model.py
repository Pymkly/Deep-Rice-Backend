"""
MODÈLES PYDANTIC - WATER MANAGEMENT (INTÉGRÉ)
Adapté pour la structure deeprice2: users → lands → parcels → potos

Fichier: api/water/water_model.py
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class GrowthStage(str, Enum):
    """Stades de croissance du riz"""
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    REPRODUCTIVE = "reproductive"
    MATURATION = "maturation"

class SoilType(str, Enum):
    """Types de sol"""
    CLAY = "clay"           # Argileux
    SANDY = "sandy"         # Sableux
    LOAMY = "loamy"         # Limoneux
    PEAT = "peat"           # Tourbeux

class IrrigationType(str, Enum):
    """Types d'irrigation"""
    FLOODED = "flooded"     # Inondé (traditionnel)
    SRI = "sri"             # System of Rice Intensification
    AWD = "awd"             # Alternate Wetting and Drying

# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================

class ParcelWaterConfig(BaseModel):
    """Configuration eau pour une parcelle (remplace FieldData)"""
    parcel_id: int = Field(..., description="ID de la parcelle (référence parcels.id)")
    soil_type: SoilType
    irrigation_type: IrrigationType
    planting_date: datetime
    current_growth_stage: GrowthStage
    area_hectares: Optional[float] = Field(None, gt=0, description="Surface en hectares")
    target_water_mm_per_day: float = Field(5.0, description="Cible irrigation quotidienne")
    is_active: bool = Field(True, description="Configuration active")

class FieldData(BaseModel):
    """Alias pour compatibilité (utilise ParcelWaterConfig en interne)"""
    field_id: str = Field(..., description="ID parcelle sous forme string")
    location: str = Field(..., description="Localisation (hérité de parcels)")
    area_hectares: float = Field(..., gt=0, description="Surface en hectares")
    soil_type: SoilType
    irrigation_type: IrrigationType
    planting_date: datetime
    current_growth_stage: GrowthStage

class WeatherData(BaseModel):
    """Données météorologiques"""
    date: datetime
    temperature_celsius: float = Field(..., ge=-10, le=50)
    humidity_percent: float = Field(..., ge=0, le=100)
    rainfall_mm: float = Field(..., ge=0)
    evapotranspiration_mm: Optional[float] = Field(None, ge=0)
    wind_speed_kmh: Optional[float] = Field(None, ge=0)
    solar_radiation_mj: Optional[float] = Field(None, ge=0)

class SoilMoistureData(BaseModel):
    """Données d'humidité du sol (capteurs IoT sur POTOs)"""
    sensor_id: str
    poto_id: int = Field(..., description="ID du POTO où le capteur est installé")
    timestamp: datetime
    moisture_percent: float = Field(..., ge=0, le=100)
    soil_temperature_celsius: float
    depth_cm: int = Field(..., description="Profondeur du capteur en cm")
    battery_level_percent: Optional[float] = Field(None, ge=0, le=100)

    # Pour compatibilité backend (field_id sera déduit du poto_id)
    field_id: Optional[str] = None

class WaterPredictionRequest(BaseModel):
    """Requête de prédiction des besoins en eau"""
    field_id: str = Field(..., description="ID parcelle (parcel_id sous forme string)")
    weather_forecast: List[WeatherData] = Field(..., max_length=7, description="Prévisions 7 jours")
    current_soil_moisture: Optional[float] = Field(None, ge=0, le=100)

class WaterPredictionResponse(BaseModel):
    """Réponse de prédiction"""
    field_id: str = Field(..., description="ID parcelle")
    prediction_date: datetime
    daily_predictions: List[dict] = Field(..., description="Prédictions journalières")
    total_water_needed_mm: float
    confidence_score: float = Field(..., ge=0, le=1)

class IrrigationRecommendation(BaseModel):
    """Recommandation d'irrigation"""
    field_id: str = Field(..., description="ID parcelle")
    recommendation_date: datetime
    should_irrigate: bool
    water_amount_mm: float = Field(..., ge=0)
    timing: str = Field(..., description="Moment optimal (morning/evening)")
    reason: str
    priority: str = Field(..., description="low/medium/high/critical")

class WaterAlert(BaseModel):
    """Alerte hydrique"""
    alert_id: str
    field_id: str = Field(..., description="ID parcelle")
    alert_type: str = Field(..., description="drought/flood/optimal/sensor_offline")
    severity: str = Field(..., description="info/warning/critical")
    message: str
    timestamp: datetime
    action_required: Optional[str] = None
    is_resolved: bool = Field(False)
    resolved_at: Optional[datetime] = None

class WaterStatistics(BaseModel):
    """Statistiques de consommation d'eau"""
    field_id: str = Field(..., description="ID parcelle")
    period_start: datetime
    period_end: datetime
    total_water_used_mm: float
    total_rainfall_mm: float
    irrigation_events: int
    water_efficiency: float = Field(..., description="Rendement/eau ratio")
    savings_vs_traditional_percent: float
    avg_soil_moisture: Optional[float] = Field(None, description="Humidité moyenne du sol")

class IrrigationEvent(BaseModel):
    """Événement d'irrigation enregistré"""
    parcel_id: int
    event_date: datetime
    water_applied_mm: float = Field(..., gt=0)
    irrigation_method: Optional[str] = Field(None, description="manual/automatic/rainfall")
    duration_minutes: Optional[int] = None
    source: Optional[str] = Field(None, description="well/river/canal/rain")
    recorded_by: Optional[int] = Field(None, description="User ID")
    notes: Optional[str] = None

# ============================================================================
# MODÈLES DE RÉPONSE API
# ============================================================================

class ParcelSummary(BaseModel):
    """Résumé d'une parcelle avec infos water"""
    parcel_id: int
    parcel_name: str
    land_name: str
    owner_name: str
    owner_email: str
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    current_growth_stage: Optional[str] = None
    planting_date: Optional[datetime] = None
    area_hectares: Optional[float] = None
    is_active: Optional[bool] = None
    poto_count: int = 0
    sensor_readings_count: int = 0
    predictions_count: int = 0
    active_alerts_count: int = 0
    last_sensor_reading: Optional[datetime] = None
    created_at: Optional[datetime] = None

class SensorReading(BaseModel):
    """Lecture de capteur avec contexte"""
    id: int
    sensor_id: str
    poto_id: int
    poto_ref: str
    parcel_id: int
    parcel_name: str
    timestamp: datetime
    moisture_percent: float
    soil_temperature_celsius: float
    depth_cm: int
    battery_level_percent: Optional[float] = None

class HealthCheckResponse(BaseModel):
    """Réponse health check"""
    status: str
    database: str
    model: str
    timestamp: datetime
    error: Optional[str] = None
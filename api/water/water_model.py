from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

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

class FieldData(BaseModel):
    """Données du champ de riz"""
    field_id: str = Field(..., description="Identifiant unique du champ")
    location: str = Field(..., description="Localisation (lat,lon ou nom)")
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

class SoilMoistureData(BaseModel):
    """Données d'humidité du sol (capteurs IoT)"""
    sensor_id: str
    field_id: str
    timestamp: datetime
    moisture_percent: float = Field(..., ge=0, le=100)
    soil_temperature_celsius: float
    depth_cm: int = Field(..., description="Profondeur du capteur")

class WaterPredictionRequest(BaseModel):
    """Requête de prédiction des besoins en eau"""
    field_id: str
    weather_forecast: List[WeatherData] = Field(..., max_items=7, description="Prévisions 7 jours")
    current_soil_moisture: Optional[float] = Field(None, ge=0, le=100)

class WaterPredictionResponse(BaseModel):
    """Réponse de prédiction"""
    field_id: str
    prediction_date: datetime
    daily_predictions: List[dict] = Field(..., description="Prédictions journalières")
    total_water_needed_mm: float
    confidence_score: float = Field(..., ge=0, le=1)

class IrrigationRecommendation(BaseModel):
    """Recommandation d'irrigation"""
    field_id: str
    recommendation_date: datetime
    should_irrigate: bool
    water_amount_mm: float = Field(..., ge=0)
    timing: str = Field(..., description="Moment optimal (morning/evening)")
    reason: str
    priority: str = Field(..., description="low/medium/high/critical")

class WaterAlert(BaseModel):
    """Alerte hydrique"""
    alert_id: str
    field_id: str
    alert_type: str = Field(..., description="drought/flood/optimal")
    severity: str = Field(..., description="info/warning/critical")
    message: str
    timestamp: datetime
    action_required: Optional[str] = None

class WaterStatistics(BaseModel):
    """Statistiques de consommation d'eau"""
    field_id: str
    period_start: datetime
    period_end: datetime
    total_water_used_mm: float
    total_rainfall_mm: float
    irrigation_events: int
    water_efficiency: float = Field(..., description="Rendement/eau ratio")
    savings_vs_traditional_percent: float

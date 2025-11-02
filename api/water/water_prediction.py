import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
from typing import List, Optional
import uuid 
from api.water.water_model import * 

class WaterPredictor:
    """Classe principale pour les prédictions et recommandations d'eau"""
    
    def __init__(self, model_path: str):
        """Charge le modèle ML"""
        try:
            self.model = tf.keras.models.load_model(model_path)
            print(f"✅ Modèle chargé: {model_path}")
        except Exception as e:
            print(f"⚠️ Modèle non trouvé, mode démo activé: {e}")
            self.model = None
    
    def predict(self, field_id: str, weather_data: List[WeatherData], 
                soil_moisture: Optional[float] = None) -> WaterPredictionResponse:
        """Prédit les besoins en eau pour 7 jours"""
        
        daily_predictions = []
        total_water = 0.0
        
        for i, weather in enumerate(weather_data):
            # Préparation des features
            features = self._prepare_features(weather, soil_moisture)
            
            # Prédiction (mode démo si pas de modèle)
            if self.model:
                water_needed = float(self.model.predict(features)[0][0])
            else:
                # Formule simplifiée pour démo
                water_needed = self._simple_water_calculation(weather, soil_moisture)
            
            daily_predictions.append({
                "date": weather.date.isoformat(),
                "water_needed_mm": round(water_needed, 2),
                "temperature": weather.temperature_celsius,
                "rainfall": weather.rainfall_mm,
                "net_irrigation_mm": max(0, water_needed - weather.rainfall_mm)
            })
            
            total_water += water_needed
        
        return WaterPredictionResponse(
            field_id=field_id,
            prediction_date=datetime.now(),
            daily_predictions=daily_predictions,
            total_water_needed_mm=round(total_water, 2),
            confidence_score=0.85 if self.model else 0.60
        )
    
    def generate_recommendations(self, field_id: str, days: int) -> List[IrrigationRecommendation]:
        """Génère des recommandations d'irrigation"""
        recommendations = []
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            
            # Logique de recommandation (simplifié)
            should_irrigate = i % 3 == 0  # Ex: tous les 3 jours
            water_amount = 50 if should_irrigate else 0
            priority = "high" if i < 2 else "medium"
            
            rec = IrrigationRecommendation(
                field_id=field_id,
                recommendation_date=date,
                should_irrigate=should_irrigate,
                water_amount_mm=water_amount,
                timing="morning",
                reason="Maintien humidité optimale" if should_irrigate else "Humidité suffisante",
                priority=priority
            )
            recommendations.append(rec)
        
        return recommendations
    
    def get_active_alerts(self, field_id: str) -> List[WaterAlert]:
        """Récupère les alertes actives"""
        # TODO: Logique d'alerte basée sur seuils
        alerts = []
        
        # Exemple d'alerte
        if np.random.random() > 0.7:  # 30% de chance d'alerte
            alert = WaterAlert(
                alert_id=str(uuid.uuid4()),
                field_id=field_id,
                alert_type="drought",
                severity="warning",
                message="Niveau d'humidité du sol en baisse. Irrigation recommandée dans 24h.",
                timestamp=datetime.now(),
                action_required="Planifier irrigation de 40mm"
            )
            alerts.append(alert)
        
        return alerts
    
    def calculate_statistics(self, field_id: str, start_date: datetime, 
                            end_date: datetime) -> WaterStatistics:
        """Calcule les statistiques de consommation"""
        # TODO: Récupérer données réelles de la DB
        days = (end_date - start_date).days
        
        return WaterStatistics(
            field_id=field_id,
            period_start=start_date,
            period_end=end_date,
            total_water_used_mm=days * 45,  # Exemple
            total_rainfall_mm=days * 15,
            irrigation_events=days // 3,
            water_efficiency=4.5,  # tonnes riz / 1000 m³ eau
            savings_vs_traditional_percent=35.0
        )
    
    def _prepare_features(self, weather: WeatherData, soil_moisture: Optional[float]) -> np.ndarray:
        """Prépare les features pour le modèle"""
        features = [
            weather.temperature_celsius,
            weather.humidity_percent,
            weather.rainfall_mm,
            weather.evapotranspiration_mm or 5.0,
            soil_moisture or 60.0
        ]
        return np.array([features])
    
    def _simple_water_calculation(self, weather: WeatherData, soil_moisture: Optional[float]) -> float:
        """Calcul simplifié des besoins en eau (fallback sans modèle)"""
        base_need = 50  # mm/jour base
        
        # Ajustements
        temp_factor = (weather.temperature_celsius - 25) * 2
        humidity_factor = (80 - weather.humidity_percent) * 0.3
        moisture_factor = (60 - (soil_moisture or 60)) * 0.5
        
        water_needed = base_need + temp_factor + humidity_factor + moisture_factor
        return max(0, min(water_needed, 100))  # Entre 0 et 100 mm


"""
MODULE DE PRÉDICTION - WATER MANAGEMENT (INTÉGRÉ)
Adapté pour deeprice2: users → lands → parcels → potos

Fichier: api/water/water_prediction.py
"""

import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
from typing import List, Optional
import uuid 

from api.water.water_model import (
    WeatherData, WaterPredictionResponse, IrrigationRecommendation, 
    WaterAlert, WaterStatistics, GrowthStage
)

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
                soil_moisture: Optional[float] = None,
                growth_stage: Optional[str] = None) -> WaterPredictionResponse:
        """
        Prédit les besoins en eau pour 7 jours
        
        Args:
            field_id: ID de la parcelle (parcel_id sous forme string)
            weather_data: Liste des prévisions météo (7 jours)
            soil_moisture: Humidité actuelle du sol (%)
            growth_stage: Stade de croissance actuel
        
        Returns:
            WaterPredictionResponse avec prédictions journalières
        """
        
        daily_predictions = []
        total_water = 0.0
        
        # Facteur de croissance (besoins varient selon le stade)
        growth_factor = self._get_growth_factor(growth_stage)
        
        for i, weather in enumerate(weather_data):
            # Préparation des features
            features = self._prepare_features(weather, soil_moisture, growth_stage)
            
            # Prédiction (mode démo si pas de modèle)
            if self.model:
                try:
                    water_needed = float(self.model.predict(features, verbose=0)[0][0])
                except Exception as e:
                    print(f"⚠️ Erreur prédiction ML: {e}, fallback mode démo")
                    water_needed = self._simple_water_calculation(
                        weather, soil_moisture, growth_factor
                    )
            else:
                # Formule simplifiée pour démo
                water_needed = self._simple_water_calculation(
                    weather, soil_moisture, growth_factor
                )
            
            # Calcul irrigation nette (eau nécessaire - pluie)
            net_irrigation = max(0, water_needed - weather.rainfall_mm)
            
            # Ajuster soil_moisture pour le jour suivant (simulation)
            if soil_moisture is not None:
                soil_moisture = self._update_soil_moisture(
                    soil_moisture, water_needed, weather.rainfall_mm
                )
            
            daily_predictions.append({
                "date": weather.date.isoformat(),
                "water_needed_mm": round(water_needed, 2),
                "temperature": weather.temperature_celsius,
                "humidity": weather.humidity_percent,
                "rainfall": weather.rainfall_mm,
                "evapotranspiration_mm": weather.evapotranspiration_mm or 5.0,
                "net_irrigation_mm": round(net_irrigation, 2),
                "confidence_score": 0.87 if self.model else 0.65
            })
            
            total_water += water_needed
        
        return WaterPredictionResponse(
            field_id=field_id,
            prediction_date=datetime.now(),
            daily_predictions=daily_predictions,
            total_water_needed_mm=round(total_water, 2),
            confidence_score=0.85 if self.model else 0.62
        )
    
    def generate_recommendations(self, field_id: str, days: int,
                                soil_moisture: Optional[float] = None,
                                growth_stage: Optional[str] = None) -> List[IrrigationRecommendation]:
        """
        Génère des recommandations d'irrigation
        
        Args:
            field_id: ID de la parcelle
            days: Nombre de jours de recommandations
            soil_moisture: Humidité actuelle du sol
            growth_stage: Stade de croissance
        
        Returns:
            Liste de recommandations d'irrigation
        """
        recommendations = []
        
        # Seuils selon le stade de croissance
        thresholds = self._get_irrigation_thresholds(growth_stage)
        current_moisture = soil_moisture or 65.0
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            
            # Déterminer si irrigation nécessaire
            should_irrigate = False
            water_amount = 0.0
            priority = "low"
            reason = "Humidité du sol suffisante"
            timing = "morning"
            
            # Logique de décision
            if current_moisture < thresholds['critical']:
                should_irrigate = True
                water_amount = 60.0
                priority = "critical"
                reason = f"Humidité critique ({current_moisture:.1f}%). Irrigation urgente requise."
                
            elif current_moisture < thresholds['low']:
                should_irrigate = True
                water_amount = 50.0
                priority = "high"
                reason = f"Humidité basse ({current_moisture:.1f}%). Irrigation recommandée."
                
            elif current_moisture < thresholds['optimal']:
                should_irrigate = True
                water_amount = 40.0
                priority = "medium"
                reason = f"Humidité sous-optimale ({current_moisture:.1f}%). Irrigation préventive."
            
            # Ajuster le timing selon la température simulée
            if i % 2 == 0:  # Simulation: journées chaudes
                timing = "morning"  # Irriguer le matin
            else:
                timing = "evening"  # Irriguer le soir
            
            rec = IrrigationRecommendation(
                field_id=field_id,
                recommendation_date=date,
                should_irrigate=should_irrigate,
                water_amount_mm=water_amount,
                timing=timing,
                reason=reason,
                priority=priority
            )
            recommendations.append(rec)
            
            # Simuler évolution de l'humidité
            if should_irrigate:
                current_moisture = min(85.0, current_moisture + water_amount * 0.6)
            else:
                current_moisture = max(40.0, current_moisture - 3.0)  # Évaporation
        
        return recommendations
    
    def get_active_alerts(self, field_id: str, 
                         soil_moisture: Optional[float] = None,
                         last_sensor_reading: Optional[datetime] = None) -> List[WaterAlert]:
        """
        Génère des alertes basées sur les conditions actuelles
        
        Args:
            field_id: ID de la parcelle
            soil_moisture: Humidité actuelle du sol
            last_sensor_reading: Date de la dernière lecture capteur
        
        Returns:
            Liste des alertes actives
        """
        alerts = []
        current_time = datetime.now()
        
        # Alerte capteur hors ligne
        if last_sensor_reading:
            hours_since_reading = (current_time - last_sensor_reading).total_seconds() / 3600
            if hours_since_reading > 6:
                alert = WaterAlert(
                    alert_id=f"ALERT-{uuid.uuid4()}",
                    field_id=field_id,
                    alert_type="sensor_offline",
                    severity="warning" if hours_since_reading < 24 else "critical",
                    message=f"Aucune donnée capteur depuis {int(hours_since_reading)} heures",
                    timestamp=current_time,
                    action_required="Vérifier la batterie et la connexion du capteur"
                )
                alerts.append(alert)
        
        # Alertes basées sur l'humidité du sol
        if soil_moisture is not None:
            if soil_moisture < 45:
                alert = WaterAlert(
                    alert_id=f"ALERT-{uuid.uuid4()}",
                    field_id=field_id,
                    alert_type="drought",
                    severity="critical",
                    message=f"Sécheresse critique détectée: {soil_moisture:.1f}% d'humidité",
                    timestamp=current_time,
                    action_required=f"Irrigation urgente de 60mm recommandée immédiatement"
                )
                alerts.append(alert)
                
            elif soil_moisture < 55:
                alert = WaterAlert(
                    alert_id=f"ALERT-{uuid.uuid4()}",
                    field_id=field_id,
                    alert_type="drought",
                    severity="warning",
                    message=f"Niveau d'humidité bas: {soil_moisture:.1f}%",
                    timestamp=current_time,
                    action_required=f"Planifier irrigation de 50mm dans les 24h"
                )
                alerts.append(alert)
                
            elif soil_moisture > 85:
                alert = WaterAlert(
                    alert_id=f"ALERT-{uuid.uuid4()}",
                    field_id=field_id,
                    alert_type="flood",
                    severity="warning",
                    message=f"Excès d'eau détecté: {soil_moisture:.1f}% d'humidité",
                    timestamp=current_time,
                    action_required="Améliorer le drainage, arrêter l'irrigation"
                )
                alerts.append(alert)
                
            elif 60 <= soil_moisture <= 75:
                alert = WaterAlert(
                    alert_id=f"ALERT-{uuid.uuid4()}",
                    field_id=field_id,
                    alert_type="optimal",
                    severity="info",
                    message=f"Conditions optimales: {soil_moisture:.1f}% d'humidité",
                    timestamp=current_time,
                    action_required=None
                )
                alerts.append(alert)
        
        return alerts
    
    def calculate_statistics(self, field_id: str, start_date: datetime, 
                            end_date: datetime) -> WaterStatistics:
        """
        Calcule les statistiques de consommation (simulation si pas de données)
        
        Args:
            field_id: ID de la parcelle
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            WaterStatistics avec les stats calculées
        """
        days = (end_date - start_date).days
        
        # Simulation (dans la vraie implémentation, ces données viennent de la DB)
        total_water_used = days * 5.2  # mm/jour moyen
        total_rainfall = days * 2.5  # mm/jour moyen
        irrigation_events = days // 3  # Irrigation tous les 3 jours
        
        # Calcul efficience
        water_efficiency = 4.5  # kg riz / m³ eau
        savings_vs_traditional = 32.0  # % économie vs méthode traditionnelle
        avg_soil_moisture = 65.0
        
        return WaterStatistics(
            field_id=field_id,
            period_start=start_date,
            period_end=end_date,
            total_water_used_mm=total_water_used,
            total_rainfall_mm=total_rainfall,
            irrigation_events=irrigation_events,
            water_efficiency=water_efficiency,
            savings_vs_traditional_percent=savings_vs_traditional,
            avg_soil_moisture=avg_soil_moisture
        )
    
    # ========================================================================
    # MÉTHODES PRIVÉES
    # ========================================================================
    
    def _get_growth_factor(self, growth_stage: Optional[str]) -> float:
        """Retourne le facteur multiplicateur selon le stade de croissance"""
        factors = {
            GrowthStage.GERMINATION.value: 0.7,      # Besoins faibles
            GrowthStage.VEGETATIVE.value: 1.2,       # Besoins élevés
            GrowthStage.REPRODUCTIVE.value: 1.4,     # Besoins maximaux
            GrowthStage.MATURATION.value: 0.8        # Besoins réduits
        }
        return factors.get(growth_stage, 1.0)
    
    def _get_irrigation_thresholds(self, growth_stage: Optional[str]) -> dict:
        """Retourne les seuils d'humidité selon le stade"""
        base_thresholds = {
            'critical': 45,
            'low': 55,
            'optimal': 65,
            'high': 80
        }
        
        # Ajuster selon le stade
        if growth_stage == GrowthStage.REPRODUCTIVE.value:
            # Stade reproductif nécessite plus d'eau
            base_thresholds['critical'] = 50
            base_thresholds['low'] = 60
            base_thresholds['optimal'] = 70
        
        return base_thresholds
    
    def _prepare_features(self, weather: WeatherData, 
                         soil_moisture: Optional[float],
                         growth_stage: Optional[str]) -> np.ndarray:
        """Prépare les features pour le modèle ML"""
        
        # Encoder le stade de croissance
        growth_encoded = {
            GrowthStage.GERMINATION.value: 0,
            GrowthStage.VEGETATIVE.value: 1,
            GrowthStage.REPRODUCTIVE.value: 2,
            GrowthStage.MATURATION.value: 3
        }.get(growth_stage, 1)
        
        features = [
            weather.temperature_celsius,
            weather.humidity_percent,
            weather.rainfall_mm,
            weather.evapotranspiration_mm or 5.0,
            soil_moisture or 65.0,
            growth_encoded,
            weather.wind_speed_kmh or 10.0,
            weather.solar_radiation_mj or 22.0
        ]
        
        return np.array([features])
    
    def _simple_water_calculation(self, weather: WeatherData, 
                                  soil_moisture: Optional[float],
                                  growth_factor: float = 1.0) -> float:
        """
        Calcul simplifié des besoins en eau (fallback sans modèle)
        
        Formule basée sur:
        - Évapotranspiration de référence (ET0)
        - Coefficient cultural (Kc) selon stade
        - Ajustements température, humidité, vent
        """
        
        # Base: Évapotranspiration
        et0 = weather.evapotranspiration_mm or 5.0
        
        # Coefficient cultural (varie avec stade de croissance)
        kc = 1.0 * growth_factor
        
        # ETc = ET0 * Kc
        water_needed = et0 * kc
        
        # Ajustement température (au-dessus de 30°C augmente les besoins)
        if weather.temperature_celsius > 30:
            temp_adjustment = (weather.temperature_celsius - 30) * 0.5
            water_needed += temp_adjustment
        
        # Ajustement humidité (air sec augmente évaporation)
        if weather.humidity_percent < 60:
            humidity_adjustment = (60 - weather.humidity_percent) * 0.1
            water_needed += humidity_adjustment
        
        # Ajustement humidité du sol
        if soil_moisture is not None:
            if soil_moisture < 55:
                # Sol sec: augmenter irrigation
                water_needed *= 1.3
            elif soil_moisture > 75:
                # Sol humide: réduire irrigation
                water_needed *= 0.7
        
        # Ajustement vent (vent fort augmente évaporation)
        if weather.wind_speed_kmh and weather.wind_speed_kmh > 15:
            wind_adjustment = (weather.wind_speed_kmh - 15) * 0.2
            water_needed += wind_adjustment
        
        # Limites raisonnables
        water_needed = max(2.0, min(water_needed, 12.0))
        
        return water_needed
    
    def _update_soil_moisture(self, current_moisture: float, 
                             water_added: float, rainfall: float) -> float:
        """
        Simule l'évolution de l'humidité du sol
        
        Args:
            current_moisture: Humidité actuelle (%)
            water_added: Eau apportée par irrigation (mm)
            rainfall: Pluie (mm)
        
        Returns:
            Nouvelle humidité estimée (%)
        """
        
        # Conversion simplifiée: 10mm d'eau ≈ 5% d'augmentation humidité
        total_water = water_added + rainfall
        moisture_increase = total_water * 0.5
        
        # Percolation/évaporation (perte de 3% par jour)
        moisture_loss = 3.0
        
        new_moisture = current_moisture + moisture_increase - moisture_loss
        
        # Limites physiques
        return max(30.0, min(new_moisture, 95.0))
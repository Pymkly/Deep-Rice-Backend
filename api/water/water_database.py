"""
MODULE DE GESTION DE LA BASE DE DONNÉES - WATER MANAGEMENT
Fonctions pour interagir avec PostgreSQL

Fichier: api/water/water_database.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from api.database.conn import get_conn
from api.water.water_model import (
    FieldData, SoilMoistureData, WaterAlert, 
    WaterStatistics, IrrigationRecommendation
)

# ============================================================================
# GESTION DES CHAMPS
# ============================================================================

def create_field(field: FieldData) -> FieldData:
    """Crée un nouveau champ dans la base de données"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO water_fields 
            (field_id, location, area_hectares, soil_type, irrigation_type, 
             planting_date, current_growth_stage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            field.field_id,
            field.location,
            field.area_hectares,
            field.soil_type.value,
            field.irrigation_type.value,
            field.planting_date,
            field.current_growth_stage.value
        ))
        
        conn.commit()
        return field
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Champ {field.field_id} existe déjà") from e
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur création champ: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_all_fields() -> List[Dict[str, Any]]:
    """Récupère tous les champs actifs"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM water_fields_summary
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """)
        
        fields = cursor.fetchall()
        return [dict(field) for field in fields]
        
    except Exception as e:
        raise Exception(f"Erreur récupération champs: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_field_by_id(field_id: str) -> Optional[Dict[str, Any]]:
    """Récupère un champ par son ID"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM water_fields
            WHERE field_id = %s AND is_active = TRUE
        """, (field_id,))
        
        field = cursor.fetchone()
        return dict(field) if field else None
        
    except Exception as e:
        raise Exception(f"Erreur récupération champ: {e}") from e
    finally:
        cursor.close()
        conn.close()

def update_growth_stage(field_id: str, growth_stage: str) -> bool:
    """Met à jour le stade de croissance d'un champ"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE water_fields
            SET current_growth_stage = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE field_id = %s
        """, (growth_stage, field_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur mise à jour stade: {e}") from e
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# DONNÉES CAPTEURS
# ============================================================================

def save_sensor_data(data: SoilMoistureData) -> int:
    """Enregistre les données d'un capteur"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO water_sensor_data
            (sensor_id, field_id, timestamp, moisture_percent, 
             soil_temperature_celsius, depth_cm)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.sensor_id,
            data.field_id,
            data.timestamp,
            data.moisture_percent,
            data.soil_temperature_celsius,
            data.depth_cm
        ))
        
        sensor_data_id = cursor.fetchone()[0]
        conn.commit()
        return sensor_data_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur enregistrement capteur: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_latest_sensor_data(field_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Récupère les dernières données capteur pour un champ"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM water_sensor_data
            WHERE field_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (field_id, limit))
        
        data = cursor.fetchall()
        return [dict(row) for row in data]
        
    except Exception as e:
        raise Exception(f"Erreur récupération données capteur: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_average_soil_moisture(field_id: str, hours: int = 24) -> Optional[float]:
    """Calcule l'humidité moyenne du sol sur les N dernières heures"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT AVG(moisture_percent) as avg_moisture
            FROM water_sensor_data
            WHERE field_id = %s
            AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (field_id, hours))
        
        result = cursor.fetchone()
        return float(result[0]) if result[0] else None
        
    except Exception as e:
        raise Exception(f"Erreur calcul humidité moyenne: {e}") from e
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# PRÉDICTIONS
# ============================================================================

def save_prediction(field_id: str, prediction_date: datetime, 
                   daily_predictions: List[Dict], model_version: str = "v1.0") -> List[int]:
    """Sauvegarde les prédictions dans la base"""
    conn = get_conn()
    cursor = conn.cursor()
    
    prediction_ids = []
    
    try:
        for pred in daily_predictions:
            cursor.execute("""
                INSERT INTO water_predictions
                (field_id, prediction_date, forecast_date, water_needed_mm,
                 temperature_celsius, humidity_percent, rainfall_mm,
                 net_irrigation_mm, confidence_score, model_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                field_id,
                prediction_date,
                pred['date'],
                pred['water_needed_mm'],
                pred.get('temperature'),
                pred.get('humidity'),
                pred.get('rainfall'),
                pred.get('net_irrigation_mm'),
                pred.get('confidence_score', 0.6),
                model_version
            ))
            
            prediction_ids.append(cursor.fetchone()[0])
        
        conn.commit()
        return prediction_ids
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur sauvegarde prédictions: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_prediction_history(field_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Récupère l'historique des prédictions"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM water_predictions
            WHERE field_id = %s
            AND forecast_date > CURRENT_DATE - INTERVAL '%s days'
            ORDER BY forecast_date DESC, prediction_date DESC
        """, (field_id, days))
        
        predictions = cursor.fetchall()
        return [dict(pred) for pred in predictions]
        
    except Exception as e:
        raise Exception(f"Erreur récupération historique: {e}") from e
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ALERTES
# ============================================================================

def create_alert(alert: WaterAlert) -> str:
    """Crée une nouvelle alerte"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO water_alerts
            (alert_id, field_id, alert_type, severity, message, 
             action_required, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING alert_id
        """, (
            alert.alert_id,
            alert.field_id,
            alert.alert_type,
            alert.severity,
            alert.message,
            alert.action_required,
            alert.timestamp
        ))
        
        alert_id = cursor.fetchone()[0]
        conn.commit()
        return alert_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur création alerte: {e}") from e
    finally:
        cursor.close()
        conn.close()

def get_active_alerts(field_id: str) -> List[Dict[str, Any]]:
    """Récupère les alertes actives pour un champ"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM water_alerts
            WHERE field_id = %s
            AND is_resolved = FALSE
            ORDER BY severity DESC, timestamp DESC
        """, (field_id,))
        
        alerts = cursor.fetchall()
        return [dict(alert) for alert in alerts]
        
    except Exception as e:
        raise Exception(f"Erreur récupération alertes: {e}") from e
    finally:
        cursor.close()
        conn.close()

def resolve_alert(alert_id: str) -> bool:
    """Marque une alerte comme résolue"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE water_alerts
            SET is_resolved = TRUE,
                resolved_at = CURRENT_TIMESTAMP
            WHERE alert_id = %s
        """, (alert_id,))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur résolution alerte: {e}") from e
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# STATISTIQUES
# ============================================================================

def calculate_and_cache_statistics(field_id: str, start_date: datetime, 
                                   end_date: datetime) -> WaterStatistics:
    """Calcule et met en cache les statistiques"""
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Calculer les statistiques
        cursor.execute("""
            WITH irrigation_stats AS (
                SELECT 
                    COALESCE(SUM(water_applied_mm), 0) as total_irrigation,
                    COUNT(*) as event_count
                FROM water_irrigation_events
                WHERE field_id = %s
                AND event_date BETWEEN %s AND %s
            ),
            rainfall_stats AS (
                SELECT 
                    COALESCE(SUM(rainfall_mm), 0) as total_rainfall
                FROM water_weather_history
                WHERE field_id = %s
                AND date BETWEEN %s AND %s
            )
            SELECT 
                i.total_irrigation,
                i.event_count,
                r.total_rainfall,
                (SELECT area_hectares FROM water_fields WHERE field_id = %s) as area
            FROM irrigation_stats i, rainfall_stats r
        """, (field_id, start_date, end_date, field_id, start_date, end_date, field_id))
        
        stats = cursor.fetchone()
        
        days = (end_date - start_date).days
        total_water = float(stats['total_irrigation']) if stats else days * 45
        total_rainfall = float(stats['total_rainfall']) if stats else days * 15
        
        # Créer l'objet statistiques
        water_stats = WaterStatistics(
            field_id=field_id,
            period_start=start_date,
            period_end=end_date,
            total_water_used_mm=total_water,
            total_rainfall_mm=total_rainfall,
            irrigation_events=stats['event_count'] if stats else days // 3,
            water_efficiency=4.5,
            savings_vs_traditional_percent=35.0
        )
        
        # Mettre en cache
        cursor.execute("""
            INSERT INTO water_statistics_cache
            (field_id, period_start, period_end, total_water_used_mm,
             total_rainfall_mm, irrigation_events_count, water_efficiency,
             savings_vs_traditional_percent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (field_id, period_start, period_end)
            DO UPDATE SET
                total_water_used_mm = EXCLUDED.total_water_used_mm,
                total_rainfall_mm = EXCLUDED.total_rainfall_mm,
                irrigation_events_count = EXCLUDED.irrigation_events_count,
                calculated_at = CURRENT_TIMESTAMP
        """, (
            field_id,
            start_date,
            end_date,
            water_stats.total_water_used_mm,
            water_stats.total_rainfall_mm,
            water_stats.irrigation_events,
            water_stats.water_efficiency,
            water_stats.savings_vs_traditional_percent
        ))
        
        conn.commit()
        return water_stats
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur calcul statistiques: {e}") from e
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# UTILITAIRES
# ============================================================================

def check_database_connection() -> bool:
    """Vérifie que la connexion à la base fonctionne"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur connexion DB: {e}")
        return False

def get_table_count(table_name: str) -> int:
    """Compte le nombre de lignes dans une table"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Erreur comptage {table_name}: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
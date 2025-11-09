 

-- Parcel A: Système SRI (System Rice Intensification)
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    1, -- Parcel A
    'clay',
    'sri',
    '2025-10-15 08:00:00',
    'vegetative',
    0.5,
    4.5
) ON CONFLICT (parcel_id) DO NOTHING;

-- Parcel B: Système AWD (Alternate Wetting and Drying)
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    2, -- Parcel B
    'loamy',
    'awd',
    '2025-10-20 09:00:00',
    'germination',
    0.45,
    5.0
) ON CONFLICT (parcel_id) DO NOTHING;

-- Parcel C: Système inondé traditionnel
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    3, -- Parcel C
    'clay',
    'flooded',
    '2025-10-10 07:30:00',
    'reproductive',
    0.6,
    6.0
) ON CONFLICT (parcel_id) DO NOTHING;

-- Parcel D: Système SRI avancé
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    4, -- Parcel D
    'loamy',
    'sri',
    '2025-10-18 08:30:00',
    'vegetative',
    0.8,
    4.8
) ON CONFLICT (parcel_id) DO NOTHING;

-- Parcel E: Système AWD
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    5, -- Parcel E
    'sandy',
    'awd',
    '2025-10-22 10:00:00',
    'germination',
    0.55,
    5.5
) ON CONFLICT (parcel_id) DO NOTHING;

-- Parcel F: Système traditionnel
INSERT INTO water_parcel_config (parcel_id, soil_type, irrigation_type, planting_date, current_growth_stage, area_hectares, target_water_mm_per_day)
VALUES (
    6, -- Parcel F
    'clay',
    'flooded',
    '2025-10-12 08:00:00',
    'maturation',
    0.7,
    3.5
) ON CONFLICT (parcel_id) DO NOTHING;

-- ============================================================================
-- DONNÉES CAPTEURS (associées aux POTOs)
-- ============================================================================

-- POTO 1 (Parcel A) - Dernières 48h de lectures
INSERT INTO water_sensor_data (sensor_id, poto_id, timestamp, moisture_percent, soil_temperature_celsius, depth_cm, battery_level_percent)
VALUES 
    ('SENSOR_001', 1, NOW() - INTERVAL '2 hours', 68.5, 27.3, 15, 85.0),
    ('SENSOR_001', 1, NOW() - INTERVAL '6 hours', 65.2, 26.8, 15, 85.5),
    ('SENSOR_001', 1, NOW() - INTERVAL '12 hours', 62.8, 26.5, 15, 86.0),
    ('SENSOR_001', 1, NOW() - INTERVAL '24 hours', 60.5, 25.9, 15, 87.0),
    ('SENSOR_001', 1, NOW() - INTERVAL '48 hours', 58.2, 25.5, 15, 88.0);

-- POTO 2 (Parcel B) - Dernières 48h de lectures
INSERT INTO water_sensor_data (sensor_id, poto_id, timestamp, moisture_percent, soil_temperature_celsius, depth_cm, battery_level_percent)
VALUES 
    ('SENSOR_002', 2, NOW() - INTERVAL '2 hours', 72.3, 28.1, 15, 90.0),
    ('SENSOR_002', 2, NOW() - INTERVAL '6 hours', 70.5, 27.6, 15, 90.5),
    ('SENSOR_002', 2, NOW() - INTERVAL '12 hours', 68.9, 27.2, 15, 91.0),
    ('SENSOR_002', 2, NOW() - INTERVAL '24 hours', 66.7, 26.8, 15, 92.0),
    ('SENSOR_002', 2, NOW() - INTERVAL '48 hours', 64.3, 26.3, 15, 93.0);

-- POTO 3 (Parcel A - 2ème capteur) - Dernières 48h
INSERT INTO water_sensor_data (sensor_id, poto_id, timestamp, moisture_percent, soil_temperature_celsius, depth_cm, battery_level_percent)
VALUES 
    ('SENSOR_003', 3, NOW() - INTERVAL '2 hours', 55.8, 26.9, 15, 78.0),
    ('SENSOR_003', 3, NOW() - INTERVAL '6 hours', 54.2, 26.5, 15, 78.5),
    ('SENSOR_003', 3, NOW() - INTERVAL '12 hours', 52.6, 26.1, 15, 79.0),
    ('SENSOR_003', 3, NOW() - INTERVAL '24 hours', 50.8, 25.7, 15, 80.0),
    ('SENSOR_003', 3, NOW() - INTERVAL '48 hours', 48.9, 25.3, 15, 81.0);

-- POTO 4 (Parcel B - 2ème capteur) - Dernières 48h
INSERT INTO water_sensor_data (sensor_id, poto_id, timestamp, moisture_percent, soil_temperature_celsius, depth_cm, battery_level_percent)
VALUES 
    ('SENSOR_004', 4, NOW() - INTERVAL '2 hours', 75.4, 28.5, 15, 95.0),
    ('SENSOR_004', 4, NOW() - INTERVAL '6 hours', 73.8, 28.2, 15, 95.5),
    ('SENSOR_004', 4, NOW() - INTERVAL '12 hours', 71.9, 27.8, 15, 96.0),
    ('SENSOR_004', 4, NOW() - INTERVAL '24 hours', 69.5, 27.4, 15, 97.0),
    ('SENSOR_004', 4, NOW() - INTERVAL '48 hours', 67.2, 27.0, 15, 98.0);

-- ============================================================================
-- PRÉDICTIONS (7 jours pour chaque parcelle configurée)
-- ============================================================================

-- Prédictions Parcel A (SRI - économe en eau)
INSERT INTO water_predictions (parcel_id, prediction_date, forecast_date, water_needed_mm, temperature_celsius, humidity_percent, rainfall_mm, net_irrigation_mm, evapotranspiration_mm, confidence_score, model_version)
VALUES 
    (1, NOW(), CURRENT_DATE, 4.5, 28.5, 75.0, 0.0, 4.5, 5.2, 0.89, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 1, 4.8, 29.0, 72.0, 2.0, 2.8, 5.5, 0.87, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 2, 5.2, 29.5, 70.0, 0.0, 5.2, 5.8, 0.85, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 3, 4.9, 28.8, 73.0, 1.5, 3.4, 5.4, 0.86, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 4, 5.0, 29.2, 71.0, 0.0, 5.0, 5.6, 0.84, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 5, 4.7, 28.6, 74.0, 3.0, 1.7, 5.3, 0.88, 'v1.0'),
    (1, NOW(), CURRENT_DATE + 6, 5.1, 29.1, 72.5, 0.5, 4.6, 5.7, 0.86, 'v1.0');

-- Prédictions Parcel B (AWD - gestion alternée)
INSERT INTO water_predictions (parcel_id, prediction_date, forecast_date, water_needed_mm, temperature_celsius, humidity_percent, rainfall_mm, net_irrigation_mm, evapotranspiration_mm, confidence_score, model_version)
VALUES 
    (2, NOW(), CURRENT_DATE, 5.0, 28.2, 76.0, 0.0, 5.0, 5.5, 0.91, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 1, 5.5, 28.7, 74.0, 1.0, 4.5, 5.8, 0.89, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 2, 5.8, 29.0, 72.0, 0.0, 5.8, 6.0, 0.87, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 3, 5.3, 28.5, 75.0, 2.5, 2.8, 5.6, 0.90, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 4, 5.6, 28.9, 73.0, 0.0, 5.6, 5.9, 0.88, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 5, 5.2, 28.3, 76.0, 4.0, 1.2, 5.4, 0.91, 'v1.0'),
    (2, NOW(), CURRENT_DATE + 6, 5.4, 28.6, 74.5, 0.5, 4.9, 5.7, 0.89, 'v1.0');

-- Prédictions Parcel C (Inondé - forte consommation)
INSERT INTO water_predictions (parcel_id, prediction_date, forecast_date, water_needed_mm, temperature_celsius, humidity_percent, rainfall_mm, net_irrigation_mm, evapotranspiration_mm, confidence_score, model_version)
VALUES 
    (3, NOW(), CURRENT_DATE, 6.0, 28.8, 74.0, 0.0, 6.0, 6.2, 0.88, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 1, 6.5, 29.2, 71.0, 1.5, 5.0, 6.5, 0.86, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 2, 6.8, 29.6, 69.0, 0.0, 6.8, 6.8, 0.84, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 3, 6.3, 29.0, 72.0, 2.0, 4.3, 6.3, 0.87, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 4, 6.6, 29.4, 70.0, 0.0, 6.6, 6.6, 0.85, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 5, 6.1, 28.7, 73.5, 3.5, 2.6, 6.1, 0.89, 'v1.0'),
    (3, NOW(), CURRENT_DATE + 6, 6.4, 29.1, 71.5, 0.8, 5.6, 6.4, 0.87, 'v1.0');

-- ============================================================================
-- ALERTES (quelques alertes actives et résolues)
-- ============================================================================

-- Alerte sécheresse Parcel A
INSERT INTO water_alerts (alert_id, parcel_id, alert_type, severity, message, action_required, timestamp, is_resolved)
VALUES (
    'ALERT-' || gen_random_uuid()::text,
    1,
    'drought',
    'warning',
    'Le niveau d''humidité du sol est inférieur à 55% depuis 12 heures',
    'Irriguer immédiatement avec 5mm d''eau minimum',
    NOW() - INTERVAL '6 hours',
    FALSE
);

-- Alerte conditions optimales Parcel B (résolue)
INSERT INTO water_alerts (alert_id, parcel_id, alert_type, severity, message, action_required, timestamp, is_resolved, resolved_at, resolved_by)
VALUES (
    'ALERT-' || gen_random_uuid()::text,
    2,
    'optimal',
    'info',
    'Les conditions d''humidité sont optimales pour la croissance',
    NULL,
    NOW() - INTERVAL '24 hours',
    TRUE,
    NOW() - INTERVAL '12 hours',
    1
);

-- Alerte risque inondation Parcel C
INSERT INTO water_alerts (alert_id, parcel_id, alert_type, severity, message, action_required, timestamp, is_resolved)
VALUES (
    'ALERT-' || gen_random_uuid()::text,
    3,
    'flood',
    'critical',
    'Humidité du sol supérieure à 85% - Risque d''inondation',
    'Réduire l''irrigation et améliorer le drainage',
    NOW() - INTERVAL '3 hours',
    FALSE
);

-- Alerte capteur hors ligne
INSERT INTO water_alerts (alert_id, parcel_id, alert_type, severity, message, action_required, timestamp, is_resolved)
VALUES (
    'ALERT-' || gen_random_uuid()::text,
    1,
    'sensor_offline',
    'warning',
    'Le capteur SENSOR_001 n''a pas envoyé de données depuis 6 heures',
    'Vérifier la batterie et la connexion du capteur',
    NOW() - INTERVAL '4 hours',
    FALSE
);

-- ============================================================================
-- ÉVÉNEMENTS D'IRRIGATION
-- ============================================================================

-- Parcel A - Historique d'irrigation des 7 derniers jours
INSERT INTO water_irrigation_events (parcel_id, event_date, water_applied_mm, irrigation_method, duration_minutes, source, recorded_by)
VALUES 
    (1, NOW() - INTERVAL '1 day', 5.0, 'automatic', 45, 'canal', 1),
    (1, NOW() - INTERVAL '3 days', 4.5, 'automatic', 40, 'canal', 1),
    (1, NOW() - INTERVAL '5 days', 5.2, 'manual', 50, 'well', 1),
    (1, NOW() - INTERVAL '7 days', 4.8, 'automatic', 43, 'canal', 1);

-- Parcel B - Historique d'irrigation
INSERT INTO water_irrigation_events (parcel_id, event_date, water_applied_mm, irrigation_method, duration_minutes, source, recorded_by)
VALUES 
    (2, NOW() - INTERVAL '2 days', 5.5, 'automatic', 50, 'canal', 1),
    (2, NOW() - INTERVAL '4 days', 5.8, 'manual', 55, 'river', 1),
    (2, NOW() - INTERVAL '6 days', 5.3, 'automatic', 48, 'canal', 1);

-- Parcel C - Historique d'irrigation (système inondé)
INSERT INTO water_irrigation_events (parcel_id, event_date, water_applied_mm, irrigation_method, duration_minutes, source, recorded_by)
VALUES 
    (3, NOW() - INTERVAL '1 day', 6.5, 'automatic', 60, 'canal', 1),
    (3, NOW() - INTERVAL '2 days', 6.0, 'automatic', 55, 'canal', 1),
    (3, NOW() - INTERVAL '4 days', 6.8, 'manual', 65, 'river', 1),
    (3, NOW() - INTERVAL '6 days', 6.3, 'automatic', 58, 'canal', 1);

-- Événements de pluie (enregistrés automatiquement)
INSERT INTO water_irrigation_events (parcel_id, event_date, water_applied_mm, irrigation_method, duration_minutes, source, notes)
VALUES 
    (1, NOW() - INTERVAL '2 days', 12.5, 'rainfall', 180, 'rain', 'Pluie naturelle - forte intensité'),
    (2, NOW() - INTERVAL '2 days', 12.5, 'rainfall', 180, 'rain', 'Pluie naturelle - forte intensité'),
    (3, NOW() - INTERVAL '2 days', 12.5, 'rainfall', 180, 'rain', 'Pluie naturelle - forte intensité');

-- ============================================================================
-- HISTORIQUE MÉTÉO
-- ============================================================================

-- Météo Parcel A - derniers 7 jours
INSERT INTO water_weather_history (parcel_id, date, temperature_celsius, humidity_percent, rainfall_mm, evapotranspiration_mm, wind_speed_kmh, solar_radiation_mj, data_source)
VALUES 
    (1, CURRENT_DATE, 28.5, 75.0, 0.0, 5.2, 8.5, 22.5, 'api'),
    (1, CURRENT_DATE - 1, 29.0, 72.0, 2.0, 5.5, 9.2, 23.1, 'api'),
    (1, CURRENT_DATE - 2, 28.3, 76.5, 12.5, 4.8, 7.8, 20.3, 'api'),
    (1, CURRENT_DATE - 3, 28.8, 73.5, 1.5, 5.4, 8.9, 22.8, 'api'),
    (1, CURRENT_DATE - 4, 29.2, 71.0, 0.0, 5.6, 9.5, 23.5, 'api'),
    (1, CURRENT_DATE - 5, 28.6, 74.0, 3.0, 5.0, 8.2, 21.8, 'api'),
    (1, CURRENT_DATE - 6, 29.1, 72.5, 0.5, 5.3, 9.0, 22.9, 'api');

-- Météo Parcel B - derniers 7 jours
INSERT INTO water_weather_history (parcel_id, date, temperature_celsius, humidity_percent, rainfall_mm, evapotranspiration_mm, wind_speed_kmh, solar_radiation_mj, data_source)
VALUES 
    (2, CURRENT_DATE, 28.2, 76.0, 0.0, 5.5, 8.3, 22.2, 'api'),
    (2, CURRENT_DATE - 1, 28.7, 74.0, 1.0, 5.8, 8.9, 22.9, 'api'),
    (2, CURRENT_DATE - 2, 28.0, 77.0, 12.5, 5.0, 7.5, 20.0, 'api'),
    (2, CURRENT_DATE - 3, 28.5, 75.0, 2.5, 5.6, 8.6, 22.5, 'api'),
    (2, CURRENT_DATE - 4, 28.9, 73.0, 0.0, 5.9, 9.2, 23.2, 'api'),
    (2, CURRENT_DATE - 5, 28.3, 76.0, 4.0, 5.4, 8.0, 21.5, 'api'),
    (2, CURRENT_DATE - 6, 28.6, 74.5, 0.5, 5.7, 8.8, 22.7, 'api');

-- Météo Parcel C - derniers 7 jours
INSERT INTO water_weather_history (parcel_id, date, temperature_celsius, humidity_percent, rainfall_mm, evapotranspiration_mm, wind_speed_kmh, solar_radiation_mj, data_source)
VALUES 
    (3, CURRENT_DATE, 28.8, 74.0, 0.0, 6.2, 8.7, 22.8, 'api'),
    (3, CURRENT_DATE - 1, 29.2, 71.0, 1.5, 6.5, 9.3, 23.3, 'api'),
    (3, CURRENT_DATE - 2, 28.5, 75.5, 12.5, 5.8, 8.0, 20.5, 'api'),
    (3, CURRENT_DATE - 3, 29.0, 72.0, 2.0, 6.3, 9.0, 22.9, 'api'),
    (3, CURRENT_DATE - 4, 29.4, 70.0, 0.0, 6.6, 9.6, 23.7, 'api'),
    (3, CURRENT_DATE - 5, 28.7, 73.5, 3.5, 6.1, 8.4, 22.0, 'api'),
    (3, CURRENT_DATE - 6, 29.1, 71.5, 0.8, 6.4, 9.1, 23.0, 'api');

-- ============================================================================
-- STATISTIQUES CACHÉES (pré-calculées)
-- ============================================================================

-- Stats Parcel A - derniers 30 jours
INSERT INTO water_statistics_cache (parcel_id, period_start, period_end, total_water_used_mm, total_rainfall_mm, irrigation_events_count, water_efficiency, savings_vs_traditional_percent, avg_soil_moisture)
VALUES (
    1,
    CURRENT_DATE - 30,
    CURRENT_DATE,
    145.5,
    35.2,
    15,
    0.85,
    35.5,
    62.3
);

-- Stats Parcel B - derniers 30 jours
INSERT INTO water_statistics_cache (parcel_id, period_start, period_end, total_water_used_mm, total_rainfall_mm, irrigation_events_count, water_efficiency, savings_vs_traditional_percent, avg_soil_moisture)
VALUES (
    2,
    CURRENT_DATE - 30,
    CURRENT_DATE,
    158.7,
    35.2,
    18,
    0.82,
    28.3,
    69.8
);

-- Stats Parcel C - derniers 30 jours
INSERT INTO water_statistics_cache (parcel_id, period_start, period_end, total_water_used_mm, total_rainfall_mm, irrigation_events_count, water_efficiency, savings_vs_traditional_percent, avg_soil_moisture)
VALUES (
    3,
    CURRENT_DATE - 30,
    CURRENT_DATE,
    195.2,
    35.2,
    22,
    0.75,
    12.5,
    78.5
);

-- ============================================================================
-- VÉRIFICATION DES DONNÉES
-- ============================================================================

-- Compter les enregistrements par table
SELECT 
    'water_parcel_config' as table_name, 
    COUNT(*) as row_count 
FROM water_parcel_config
UNION ALL
SELECT 'water_sensor_data', COUNT(*) FROM water_sensor_data
UNION ALL
SELECT 'water_predictions', COUNT(*) FROM water_predictions
UNION ALL
SELECT 'water_alerts', COUNT(*) FROM water_alerts
UNION ALL
SELECT 'water_irrigation_events', COUNT(*) FROM water_irrigation_events
UNION ALL
SELECT 'water_weather_history', COUNT(*) FROM water_weather_history
UNION ALL
SELECT 'water_statistics_cache', COUNT(*) FROM water_statistics_cache
ORDER BY table_name;

-- Vérifier la vue résumée
SELECT * FROM water_parcels_summary ORDER BY parcel_id;

-- Vérifier les dernières lectures de capteurs
SELECT * FROM water_latest_sensor_readings ORDER BY parcel_id, poto_id;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
-- ============================================================================
-- SCHÉMA BASE DE DONNÉES POSTGRESQL - MODULE GESTION DE L'EAU (INTÉGRÉ)
-- Deep Rice Backend - Water Management Integration
-- Base: deeprice2
-- ============================================================================
-- 
-- Usage:
--   psql -U postgres -d deeprice2 -f 001-water-structure.sql
--
-- Ce script intègre le module Water dans la structure existante:
--   users → lands → parcels → potos
--
-- ============================================================================

-- ============================================================================
-- TABLE 1: water_parcel_config (Configuration eau par parcelle)
-- ============================================================================
-- Remplace water_fields en utilisant les parcels existants

CREATE TABLE IF NOT EXISTS water_parcel_config (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL UNIQUE REFERENCES parcels(id) ON DELETE CASCADE,
    soil_type VARCHAR(20) NOT NULL CHECK (soil_type IN ('clay', 'sandy', 'loamy', 'peat')),
    irrigation_type VARCHAR(20) NOT NULL CHECK (irrigation_type IN ('flooded', 'sri', 'awd')),
    planting_date TIMESTAMP NOT NULL,
    current_growth_stage VARCHAR(20) NOT NULL CHECK (current_growth_stage IN ('germination', 'vegetative', 'reproductive', 'maturation')),
    area_hectares DECIMAL(10, 2) CHECK (area_hectares > 0),
    target_water_mm_per_day DECIMAL(6, 2) DEFAULT 5.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_parcel_config IS 'Configuration de gestion de l''eau par parcelle';
COMMENT ON COLUMN water_parcel_config.soil_type IS 'clay=argileux, sandy=sableux, loamy=limoneux, peat=tourbeux';
COMMENT ON COLUMN water_parcel_config.irrigation_type IS 'flooded=inondé, sri=System Rice Intensification, awd=Alternate Wetting Drying';
COMMENT ON COLUMN water_parcel_config.current_growth_stage IS 'Stade de croissance actuel du riz';

CREATE INDEX idx_water_parcel_active ON water_parcel_config(is_active);
CREATE INDEX idx_water_parcel_stage ON water_parcel_config(current_growth_stage);

-- ============================================================================
-- TABLE 2: water_sensor_data (Données capteurs IoT)
-- ============================================================================
-- Les capteurs sont associés aux POTOs (points de mesure dans les parcelles)

CREATE TABLE IF NOT EXISTS water_sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    poto_id INTEGER NOT NULL REFERENCES potos(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    moisture_percent DECIMAL(5, 2) NOT NULL CHECK (moisture_percent >= 0 AND moisture_percent <= 100),
    soil_temperature_celsius DECIMAL(5, 2) NOT NULL,
    depth_cm INTEGER NOT NULL CHECK (depth_cm > 0),
    battery_level_percent DECIMAL(5, 2) CHECK (battery_level_percent >= 0 AND battery_level_percent <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_sensor_data IS 'Données des capteurs d''humidité du sol associés aux POTOs';
COMMENT ON COLUMN water_sensor_data.poto_id IS 'Point de mesure (POTO) où le capteur est installé';
COMMENT ON COLUMN water_sensor_data.depth_cm IS 'Profondeur du capteur en centimètres';

CREATE INDEX idx_sensor_poto_time ON water_sensor_data(poto_id, timestamp DESC);
CREATE INDEX idx_sensor_id ON water_sensor_data(sensor_id);
CREATE INDEX idx_sensor_timestamp ON water_sensor_data(timestamp DESC);

-- ============================================================================
-- TABLE 3: water_predictions (Historique des prédictions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_predictions (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    prediction_date TIMESTAMP NOT NULL,
    forecast_date DATE NOT NULL,
    water_needed_mm DECIMAL(6, 2) NOT NULL CHECK (water_needed_mm >= 0),
    temperature_celsius DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    rainfall_mm DECIMAL(6, 2),
    net_irrigation_mm DECIMAL(6, 2),
    evapotranspiration_mm DECIMAL(5, 2),
    confidence_score DECIMAL(4, 3) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version VARCHAR(20) DEFAULT 'v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_predictions IS 'Historique des prédictions de besoins en eau par parcelle';
COMMENT ON COLUMN water_predictions.prediction_date IS 'Date à laquelle la prédiction a été faite';
COMMENT ON COLUMN water_predictions.forecast_date IS 'Date pour laquelle la prédiction est faite';
COMMENT ON COLUMN water_predictions.net_irrigation_mm IS 'Irrigation nette recommandée = water_needed - rainfall';

CREATE INDEX idx_predictions_parcel_date ON water_predictions(parcel_id, forecast_date DESC);
CREATE INDEX idx_predictions_created ON water_predictions(created_at DESC);

-- ============================================================================
-- TABLE 4: water_alerts (Alertes hydriques)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(36) UNIQUE NOT NULL,
    parcel_id INTEGER NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('drought', 'flood', 'optimal', 'sensor_offline')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    action_required TEXT,
    timestamp TIMESTAMP NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_alerts IS 'Alertes générées par le système pour chaque parcelle';
COMMENT ON COLUMN water_alerts.alert_type IS 'Type: drought=sécheresse, flood=inondation, optimal=conditions optimales, sensor_offline=capteur hors ligne';
COMMENT ON COLUMN water_alerts.resolved_by IS 'Utilisateur ayant résolu l''alerte';

CREATE INDEX idx_alerts_active ON water_alerts(parcel_id, is_resolved, timestamp DESC);
CREATE INDEX idx_alerts_severity ON water_alerts(severity, is_resolved);
CREATE INDEX idx_alerts_type ON water_alerts(alert_type, is_resolved);

-- ============================================================================
-- TABLE 5: water_irrigation_events (Événements d'irrigation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_irrigation_events (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    event_date TIMESTAMP NOT NULL,
    water_applied_mm DECIMAL(6, 2) NOT NULL CHECK (water_applied_mm > 0),
    irrigation_method VARCHAR(20) CHECK (irrigation_method IN ('manual', 'automatic', 'rainfall')),
    duration_minutes INTEGER,
    source VARCHAR(50),
    recorded_by INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_irrigation_events IS 'Enregistrement des événements d''irrigation réels par parcelle';
COMMENT ON COLUMN water_irrigation_events.source IS 'Source d''eau: rain=pluie, well=puits, river=rivière, canal=canal';
COMMENT ON COLUMN water_irrigation_events.recorded_by IS 'Utilisateur ayant enregistré l''événement';

CREATE INDEX idx_irrigation_parcel_date ON water_irrigation_events(parcel_id, event_date DESC);
CREATE INDEX idx_irrigation_method ON water_irrigation_events(irrigation_method);

-- ============================================================================
-- TABLE 6: water_statistics_cache (Cache des statistiques calculées)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_statistics_cache (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_water_used_mm DECIMAL(10, 2),
    total_rainfall_mm DECIMAL(10, 2),
    irrigation_events_count INTEGER,
    water_efficiency DECIMAL(6, 2),
    savings_vs_traditional_percent DECIMAL(5, 2),
    avg_soil_moisture DECIMAL(5, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parcel_id, period_start, period_end)
);

COMMENT ON TABLE water_statistics_cache IS 'Cache des statistiques pré-calculées pour performances';

CREATE INDEX idx_stats_parcel_period ON water_statistics_cache(parcel_id, period_start, period_end);

-- ============================================================================
-- TABLE 7: water_weather_history (Historique météo)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_weather_history (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    rainfall_mm DECIMAL(6, 2),
    evapotranspiration_mm DECIMAL(5, 2),
    wind_speed_kmh DECIMAL(5, 2),
    solar_radiation_mj DECIMAL(6, 2),
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parcel_id, date)
);

COMMENT ON TABLE water_weather_history IS 'Historique des conditions météorologiques réelles par parcelle';
COMMENT ON COLUMN water_weather_history.data_source IS 'Source: sensor=capteur local, api=API météo, manual=saisie manuelle';

CREATE INDEX idx_weather_parcel_date ON water_weather_history(parcel_id, date DESC);

-- ============================================================================
-- FONCTIONS UTILITAIRES
-- ============================================================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger sur water_parcel_config
CREATE TRIGGER update_water_parcel_config_updated_at 
BEFORE UPDATE ON water_parcel_config
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue: Résumé des parcelles avec gestion de l'eau
CREATE OR REPLACE VIEW water_parcels_summary AS
SELECT 
    p.id as parcel_id,
    p.title as parcel_name,
    l.title as land_name,
    u.first_name || ' ' || u.last_name as owner_name,
    u.email as owner_email,
    wpc.soil_type,
    wpc.irrigation_type,
    wpc.current_growth_stage,
    wpc.planting_date,
    wpc.area_hectares,
    wpc.is_active,
    COUNT(DISTINCT pt.id) as poto_count,
    COUNT(DISTINCT wsd.id) as sensor_readings_count,
    COUNT(DISTINCT wp.id) as predictions_count,
    COUNT(DISTINCT wa.id) FILTER (WHERE wa.is_resolved = FALSE) as active_alerts_count,
    MAX(wsd.timestamp) as last_sensor_reading,
    wpc.created_at
FROM parcels p
JOIN lands l ON p.land_id = l.id
JOIN users u ON l.user_id = u.id
LEFT JOIN water_parcel_config wpc ON p.id = wpc.parcel_id
LEFT JOIN potos pt ON p.id = pt.parcel_id
LEFT JOIN water_sensor_data wsd ON pt.id = wsd.poto_id
LEFT JOIN water_predictions wp ON p.id = wp.parcel_id
LEFT JOIN water_alerts wa ON p.id = wa.parcel_id
GROUP BY p.id, l.title, u.first_name, u.last_name, u.email, 
         wpc.soil_type, wpc.irrigation_type, wpc.current_growth_stage,
         wpc.planting_date, wpc.area_hectares, wpc.is_active, wpc.created_at;

COMMENT ON VIEW water_parcels_summary IS 'Vue résumée avec statistiques agrégées par parcelle avec gestion eau';

-- Vue: Dernières lectures de capteurs par POTO
CREATE OR REPLACE VIEW water_latest_sensor_readings AS
SELECT DISTINCT ON (poto_id)
    wsd.id,
    wsd.sensor_id,
    wsd.poto_id,
    pt.ref as poto_ref,
    pt.parcel_id,
    p.title as parcel_name,
    wsd.timestamp,
    wsd.moisture_percent,
    wsd.soil_temperature_celsius,
    wsd.depth_cm,
    wsd.battery_level_percent
FROM water_sensor_data wsd
JOIN potos pt ON wsd.poto_id = pt.id
JOIN parcels p ON pt.parcel_id = p.id
ORDER BY wsd.poto_id, wsd.timestamp DESC;

COMMENT ON VIEW water_latest_sensor_readings IS 'Dernières lectures de capteurs pour chaque POTO';

-- ============================================================================
-- PERMISSIONS (adapter selon ton utilisateur)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deeprice_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deeprice_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO deeprice_user;

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================

-- Afficher toutes les tables Water créées
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'water_%'
ORDER BY table_name;

-- Afficher les contraintes
SELECT
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type
FROM information_schema.table_constraints AS tc
WHERE tc.table_schema = 'public'
AND tc.table_name LIKE 'water_%'
ORDER BY tc.table_name, tc.constraint_type;

-- Afficher les relations (foreign keys)
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name LIKE 'water_%'
ORDER BY tc.table_name;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
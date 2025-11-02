-- ============================================================================
-- SCHÉMA BASE DE DONNÉES POSTGRESQL - MODULE GESTION DE L'EAU
-- Deep Rice Backend - Water Management
-- ============================================================================
-- 
-- Usage:
--   1. Connecte-toi à PostgreSQL : psql -U root -d deeprice
--   2. Execute ce script : \i base/postgresql/relation/000070-water.sql
--
-- ============================================================================

-- ============================================================================
-- TABLE 1: water_fields (Champs de riz)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_fields (
    field_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    area_hectares DECIMAL(10, 2) NOT NULL CHECK (area_hectares > 0),
    soil_type VARCHAR(20) NOT NULL CHECK (soil_type IN ('clay', 'sandy', 'loamy', 'peat')),
    irrigation_type VARCHAR(20) NOT NULL CHECK (irrigation_type IN ('flooded', 'sri', 'awd')),
    planting_date TIMESTAMP NOT NULL,
    current_growth_stage VARCHAR(20) NOT NULL CHECK (current_growth_stage IN ('germination', 'vegetative', 'reproductive', 'maturation')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE water_fields IS 'Champs de riz enregistrés dans le système';
COMMENT ON COLUMN water_fields.soil_type IS 'clay=argileux, sandy=sableux, loamy=limoneux, peat=tourbeux';
COMMENT ON COLUMN water_fields.irrigation_type IS 'flooded=inondé, sri=System Rice Intensification, awd=Alternate Wetting Drying';

-- Index pour recherches fréquentes
CREATE INDEX idx_water_fields_active ON water_fields(is_active);
CREATE INDEX idx_water_fields_location ON water_fields(latitude, longitude);

-- ============================================================================
-- TABLE 2: water_sensor_data (Données capteurs IoT)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    moisture_percent DECIMAL(5, 2) NOT NULL CHECK (moisture_percent >= 0 AND moisture_percent <= 100),
    soil_temperature_celsius DECIMAL(5, 2) NOT NULL,
    depth_cm INTEGER NOT NULL CHECK (depth_cm > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_sensor_data IS 'Données des capteurs d''humidité du sol';
COMMENT ON COLUMN water_sensor_data.depth_cm IS 'Profondeur du capteur en centimètres';

-- Index pour requêtes temporelles
CREATE INDEX idx_sensor_field_time ON water_sensor_data(field_id, timestamp DESC);
CREATE INDEX idx_sensor_id ON water_sensor_data(sensor_id);

-- ============================================================================
-- TABLE 3: water_predictions (Historique des prédictions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_predictions (
    id SERIAL PRIMARY KEY,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    prediction_date TIMESTAMP NOT NULL,
    forecast_date DATE NOT NULL,
    water_needed_mm DECIMAL(6, 2) NOT NULL CHECK (water_needed_mm >= 0),
    temperature_celsius DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    rainfall_mm DECIMAL(6, 2),
    net_irrigation_mm DECIMAL(6, 2),
    confidence_score DECIMAL(4, 3) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_predictions IS 'Historique des prédictions de besoins en eau';
COMMENT ON COLUMN water_predictions.prediction_date IS 'Date à laquelle la prédiction a été faite';
COMMENT ON COLUMN water_predictions.forecast_date IS 'Date pour laquelle la prédiction est faite';

-- Index pour requêtes d'historique
CREATE INDEX idx_predictions_field_date ON water_predictions(field_id, forecast_date DESC);
CREATE INDEX idx_predictions_created ON water_predictions(created_at DESC);

-- ============================================================================
-- TABLE 4: water_alerts (Alertes hydriques)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(36) UNIQUE NOT NULL,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('drought', 'flood', 'optimal')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    action_required TEXT,
    timestamp TIMESTAMP NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_alerts IS 'Alertes générées par le système';
COMMENT ON COLUMN water_alerts.alert_type IS 'Type: drought=sécheresse, flood=inondation, optimal=conditions optimales';

-- Index pour alertes actives
CREATE INDEX idx_alerts_active ON water_alerts(field_id, is_resolved, timestamp DESC);
CREATE INDEX idx_alerts_severity ON water_alerts(severity, is_resolved);

-- ============================================================================
-- TABLE 5: water_irrigation_events (Événements d'irrigation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_irrigation_events (
    id SERIAL PRIMARY KEY,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    event_date TIMESTAMP NOT NULL,
    water_applied_mm DECIMAL(6, 2) NOT NULL CHECK (water_applied_mm > 0),
    irrigation_method VARCHAR(20),
    duration_minutes INTEGER,
    source VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE water_irrigation_events IS 'Enregistrement des événements d''irrigation réels';
COMMENT ON COLUMN water_irrigation_events.source IS 'Source d''eau: rain=pluie, manual=manuel, automatic=automatique';

-- Index pour statistiques
CREATE INDEX idx_irrigation_field_date ON water_irrigation_events(field_id, event_date DESC);

-- ============================================================================
-- TABLE 6: water_statistics_cache (Cache des statistiques calculées)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_statistics_cache (
    id SERIAL PRIMARY KEY,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_water_used_mm DECIMAL(10, 2),
    total_rainfall_mm DECIMAL(10, 2),
    irrigation_events_count INTEGER,
    water_efficiency DECIMAL(6, 2),
    savings_vs_traditional_percent DECIMAL(5, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(field_id, period_start, period_end)
);

COMMENT ON TABLE water_statistics_cache IS 'Cache des statistiques pré-calculées pour performances';

-- Index pour recherches rapides
CREATE INDEX idx_stats_field_period ON water_statistics_cache(field_id, period_start, period_end);

-- ============================================================================
-- TABLE 7: water_weather_history (Historique météo)
-- ============================================================================

CREATE TABLE IF NOT EXISTS water_weather_history (
    id SERIAL PRIMARY KEY,
    field_id VARCHAR(50) NOT NULL REFERENCES water_fields(field_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    rainfall_mm DECIMAL(6, 2),
    evapotranspiration_mm DECIMAL(5, 2),
    wind_speed_kmh DECIMAL(5, 2),
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(field_id, date)
);

COMMENT ON TABLE water_weather_history IS 'Historique des conditions météorologiques réelles';
COMMENT ON COLUMN water_weather_history.data_source IS 'Source: sensor=capteur local, api=API météo, manual=saisie manuelle';

-- Index pour requêtes temporelles
CREATE INDEX idx_weather_field_date ON water_weather_history(field_id, date DESC);

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

-- Trigger sur water_fields
CREATE TRIGGER update_water_fields_updated_at BEFORE UPDATE ON water_fields
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VUE: water_fields_summary (Vue résumée des champs)
-- ============================================================================

CREATE OR REPLACE VIEW water_fields_summary AS
SELECT 
    f.field_id,
    f.location,
    f.area_hectares,
    f.soil_type,
    f.irrigation_type,
    f.current_growth_stage,
    f.planting_date,
    COALESCE(COUNT(DISTINCT s.id), 0) as sensor_readings_count,
    COALESCE(COUNT(DISTINCT p.id), 0) as predictions_count,
    COALESCE(COUNT(DISTINCT a.id) FILTER (WHERE a.is_resolved = FALSE), 0) as active_alerts_count,
    COALESCE(MAX(s.timestamp), NULL) as last_sensor_reading,
    f.created_at,
    f.is_active
FROM water_fields f
LEFT JOIN water_sensor_data s ON f.field_id = s.field_id
LEFT JOIN water_predictions p ON f.field_id = p.field_id
LEFT JOIN water_alerts a ON f.field_id = a.field_id
GROUP BY f.field_id;

COMMENT ON VIEW water_fields_summary IS 'Vue résumée avec statistiques agrégées par champ';

-- ============================================================================
-- DONNÉES DE TEST (optionnel)
-- ============================================================================

-- Insertion de champs de test
INSERT INTO water_fields (field_id, location, latitude, longitude, area_hectares, soil_type, irrigation_type, planting_date, current_growth_stage)
VALUES 
    ('field_test_001', 'Bongatsara, Antananarivo', -18.9333, 47.5167, 2.5, 'clay', 'sri', '2025-10-15 08:00:00', 'vegetative'),
    ('field_test_002', 'Ambohibary, Antananarivo', -18.8500, 47.5000, 1.8, 'loamy', 'awd', '2025-10-20 09:00:00', 'germination'),
    ('field_test_003', 'Ambohimangakely', -18.9000, 47.5500, 3.2, 'clay', 'flooded', '2025-10-10 07:30:00', 'reproductive')
ON CONFLICT (field_id) DO NOTHING;

-- ============================================================================
-- PERMISSIONS (adapter selon ton utilisateur)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deeprice_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deeprice_user;

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================

-- Afficher toutes les tables créées
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

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

-- Pour supprimer toutes les tables (ATTENTION: perte de données)
-- DROP TABLE IF EXISTS water_statistics_cache CASCADE;
-- DROP TABLE IF EXISTS water_irrigation_events CASCADE;
-- DROP TABLE IF EXISTS water_alerts CASCADE;
-- DROP TABLE IF EXISTS water_predictions CASCADE;
-- DROP TABLE IF EXISTS water_sensor_data CASCADE;
-- DROP TABLE IF EXISTS water_weather_history CASCADE;
-- DROP TABLE IF EXISTS water_fields CASCADE;
-- DROP VIEW IF EXISTS water_fields_summary CASCADE;
psql -U root -d deeprice -f base/postgresql/relation/000070-water.sql
base\postgresql\relation\000070-water\000070-water.sql

psql -U postgres -d deeprice -f base/postgresql/relation/000070-water/000070-water.sql
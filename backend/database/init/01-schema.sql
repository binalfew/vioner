-- ============================================================================
-- VIOLENT EVENT DATABASE SCHEMA
-- Week 7-8: Event Storage & Analytics Platform
-- ============================================================================
-- Purpose: Store and analyze events extracted from Week 3-6 NLP Pipeline
-- Author: Binalfew Kassa Mekonnen
-- Institution: Addis Ababa University
-- Date: December 2025
-- Version: 1.0
-- ============================================================================

-- This schema is optimized for the exact output format of the Week 3-6
-- rule-based NLP pipeline, matching the annotation template structure.

-- Drop existing tables (for clean installation)
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS actors CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS taxonomies CASCADE;

-- Enable UUID extension for better ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For multi-column indexes

-- ============================================================================
-- USERS TABLE (Authentication)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- Taxonomy Table (Week 1-2 hierarchical classification)
CREATE TABLE taxonomies (
    taxonomy_id SERIAL PRIMARY KEY,
    level_1 VARCHAR(100) NOT NULL,
    level_2 VARCHAR(100),
    level_3 VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(level_1, level_2, level_3)
);

-- Create index for faster taxonomy lookups
CREATE INDEX idx_taxonomies_l1 ON taxonomies(level_1);
CREATE INDEX idx_taxonomies_l2 ON taxonomies(level_2);
CREATE INDEX idx_taxonomies_l3 ON taxonomies(level_3);

-- Actors Table (Armed groups, organizations, individuals)
CREATE TABLE actors (
    actor_id SERIAL PRIMARY KEY,
    actor_name VARCHAR(255) NOT NULL UNIQUE,
    actor_type VARCHAR(100),  -- Non-state armed group, State force, Civilian, etc.
    actor_category VARCHAR(50),  -- Armed group, Militia, Government, etc.
    country VARCHAR(100),
    region VARCHAR(100),
    aliases TEXT[],  -- Array of alternative names
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actors_name ON actors USING gin(actor_name gin_trgm_ops);
CREATE INDEX idx_actors_type ON actors(actor_type);
CREATE INDEX idx_actors_country ON actors(country);

-- Locations Table (Countries, cities, regions)
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(255),
    region VARCHAR(100),
    district VARCHAR(100),
    coordinates POINT,  -- (latitude, longitude)
    population INTEGER,
    location_type VARCHAR(50),  -- City, Village, Region, District
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country, city, region)
);

CREATE INDEX idx_locations_country ON locations(country);
CREATE INDEX idx_locations_city ON locations USING gin(city gin_trgm_ops);
CREATE INDEX idx_locations_coords ON locations USING gist(coordinates);

-- ============================================================================
-- CORE EVENTS TABLE (Matches Week 3-6 Pipeline Output)
-- ============================================================================

CREATE TABLE events (
    -- Primary Key
    event_id VARCHAR(100) PRIMARY KEY,  -- From pipeline (e.g., TEST_BOKO_001_001)

    -- WHO: Actor Information
    actor_normalized VARCHAR(255),
    actor_id INTEGER REFERENCES actors(actor_id),
    actor_type VARCHAR(100),
    actor_confidence DECIMAL(3, 2) CHECK (actor_confidence >= 0 AND actor_confidence <= 1),

    -- WHOM: Victim Information
    victim_normalized VARCHAR(255),
    victim_type VARCHAR(100),
    victim_confidence DECIMAL(3, 2) CHECK (victim_confidence >= 0 AND victim_confidence <= 1),

    -- WHERE: Location Information
    location_country VARCHAR(100) NOT NULL,
    location_city VARCHAR(255),
    location_coordinates VARCHAR(50),  -- String format from pipeline
    location_id INTEGER REFERENCES locations(location_id),
    location_confidence DECIMAL(3, 2) CHECK (location_confidence >= 0 AND location_confidence <= 1),

    -- WHEN: Temporal Information
    date_normalized DATE,
    date_original VARCHAR(100),  -- Original date string from text
    date_confidence DECIMAL(3, 2) CHECK (date_confidence >= 0 AND date_confidence <= 1),

    -- WHAT: Taxonomy Classification
    taxonomy_l1 VARCHAR(100) NOT NULL,
    taxonomy_l2 VARCHAR(100),
    taxonomy_l3 VARCHAR(100),
    taxonomy_id INTEGER REFERENCES taxonomies(taxonomy_id),
    classification_confidence DECIMAL(3, 2) CHECK (classification_confidence >= 0 AND classification_confidence <= 1),

    -- HOW: Method/Weapon Information
    weapon_category VARCHAR(100),
    weapon_details TEXT,
    attack_method VARCHAR(255),

    -- Casualties
    deaths INTEGER DEFAULT 0,
    injuries INTEGER DEFAULT 0,
    total_casualties INTEGER GENERATED ALWAYS AS (deaths + injuries) STORED,

    -- Severity Assessment
    severity VARCHAR(20),  -- Critical, High, Medium, Low
    severity_score INTEGER CHECK (severity_score >= 0 AND severity_score <= 100),

    -- Event Description
    event_description TEXT NOT NULL,

    -- Quality Flags
    flagged_for_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,

    -- Extraction Metadata
    annotator_name VARCHAR(100) DEFAULT 'NLP-Pipeline-Week3-6',
    extraction_method VARCHAR(50) DEFAULT 'rule-based',
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search on event descriptions
CREATE INDEX idx_events_description_fts ON events USING gin(to_tsvector('english', event_description));

-- Indexes for common queries
CREATE INDEX idx_events_date ON events(date_normalized);
CREATE INDEX idx_events_country ON events(location_country);
CREATE INDEX idx_events_actor ON events(actor_normalized);
CREATE INDEX idx_events_victim ON events(victim_normalized);
CREATE INDEX idx_events_taxonomy_l1 ON events(taxonomy_l1);
CREATE INDEX idx_events_taxonomy_l2 ON events(taxonomy_l2);
CREATE INDEX idx_events_severity ON events(severity);
CREATE INDEX idx_events_casualties ON events(total_casualties);
CREATE INDEX idx_events_flagged ON events(flagged_for_review) WHERE flagged_for_review = TRUE;

-- Composite index for time-series analysis
CREATE INDEX idx_events_date_country ON events(date_normalized, location_country);
CREATE INDEX idx_events_date_actor ON events(date_normalized, actor_normalized);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete event view with all details
CREATE OR REPLACE VIEW v_events_complete AS
SELECT
    e.event_id,
    e.event_description,
    e.date_normalized,
    e.location_country,
    e.location_city,
    e.actor_normalized,
    a.actor_type,
    e.victim_normalized,
    e.taxonomy_l1,
    e.taxonomy_l2,
    e.taxonomy_l3,
    e.weapon_category,
    e.deaths,
    e.injuries,
    e.total_casualties,
    e.severity,
    e.actor_confidence,
    e.location_confidence,
    e.date_confidence,
    e.classification_confidence,
    e.flagged_for_review,
    e.extraction_date
FROM events e
LEFT JOIN actors a ON e.actor_id = a.actor_id;

-- High-priority events (high casualties or flagged)
CREATE OR REPLACE VIEW v_events_priority AS
SELECT *
FROM v_events_complete
WHERE deaths >= 10
   OR total_casualties >= 20
   OR flagged_for_review = TRUE
   OR severity IN ('Critical', 'High')
ORDER BY date_normalized DESC;

-- Events by country summary
CREATE OR REPLACE VIEW v_country_summary AS
SELECT
    location_country,
    COUNT(*) as total_events,
    SUM(deaths) as total_deaths,
    SUM(injuries) as total_injuries,
    SUM(total_casualties) as total_casualties,
    AVG(actor_confidence) as avg_confidence,
    MIN(date_normalized) as first_event,
    MAX(date_normalized) as last_event,
    COUNT(DISTINCT actor_normalized) as unique_actors
FROM events
GROUP BY location_country
ORDER BY total_deaths DESC;

-- Actor activity summary
CREATE OR REPLACE VIEW v_actor_summary AS
SELECT
    e.actor_normalized,
    a.actor_type,
    a.country as actor_origin,
    COUNT(*) as total_events,
    SUM(e.deaths) as total_deaths,
    SUM(e.injuries) as total_injuries,
    COUNT(DISTINCT e.location_country) as countries_operated,
    MIN(e.date_normalized) as first_event,
    MAX(e.date_normalized) as last_event,
    AVG(e.actor_confidence) as avg_confidence
FROM events e
LEFT JOIN actors a ON e.actor_id = a.actor_id
WHERE e.actor_normalized IS NOT NULL
GROUP BY e.actor_normalized, a.actor_type, a.country
ORDER BY total_deaths DESC;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to automatically update timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to tables
CREATE TRIGGER update_events_modtime
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_actors_modtime
    BEFORE UPDATE ON actors
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_locations_modtime
    BEFORE UPDATE ON locations
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Function to calculate severity based on casualties
CREATE OR REPLACE FUNCTION calculate_severity(deaths INT, injuries INT)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF deaths >= 20 OR (deaths + injuries) >= 50 THEN
        RETURN 'Critical';
    ELSIF deaths >= 10 OR (deaths + injuries) >= 20 THEN
        RETURN 'High';
    ELSIF deaths >= 5 OR (deaths + injuries) >= 10 THEN
        RETURN 'Medium';
    ELSE
        RETURN 'Low';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate severity score (0-100)
CREATE OR REPLACE FUNCTION calculate_severity_score(
    deaths INT,
    injuries INT,
    actor_conf DECIMAL,
    location_conf DECIMAL
) RETURNS INTEGER AS $$
DECLARE
    casualty_score INT;
    confidence_score INT;
    final_score INT;
BEGIN
    -- Casualty component (0-70 points)
    casualty_score := LEAST(deaths * 5 + injuries * 2, 70);

    -- Confidence component (0-30 points)
    confidence_score := ROUND((COALESCE(actor_conf, 0) + COALESCE(location_conf, 0)) / 2 * 30);

    -- Final score
    final_score := casualty_score + confidence_score;

    RETURN LEAST(final_score, 100);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA POPULATION
-- ============================================================================

-- Insert common taxonomies from Week 1-2
INSERT INTO taxonomies (level_1, level_2, level_3) VALUES
-- Political Violence
('Political Violence', 'Rebellion/Armed Insurgency', 'Armed Attack'),
('Political Violence', 'Rebellion/Armed Insurgency', 'Ambush'),
('Political Violence', 'Terrorism', 'Suicide Bombing'),
('Political Violence', 'Terrorism', 'Improvised Explosive Device'),
('Political Violence', 'Terrorism', 'Hostage Taking'),
('Political Violence', 'Election Violence', 'Pre-Election Violence'),
('Political Violence', 'Political Repression', 'Crackdown on Protests'),

-- Criminal Violence
('Criminal Violence', 'Organized Crime Violence', 'Gang Warfare'),
('Criminal Violence', 'Armed Robbery/Banditry', 'Highway Robbery'),
('Criminal Violence', 'Kidnapping for Ransom', 'Mass Abduction'),
('Criminal Violence', 'Kidnapping for Ransom', 'Targeted Kidnapping'),

-- Communal Violence
('Communal Violence', 'Ethnic/Tribal Conflict', 'Inter-Ethnic Clashes'),
('Communal Violence', 'Religious Violence', 'Sectarian Violence'),
('Communal Violence', 'Resource-Based Conflict', 'Land Dispute'),
('Communal Violence', 'Pastoralist-Farmer Clashes', 'Grazing Rights Dispute'),

-- State Violence
('State Violence Against Civilians', 'Extrajudicial Killings', 'Summary Execution'),
('State Violence Against Civilians', 'State Repression of Protests', 'Live Fire on Protesters'),
('State Violence Against Civilians', 'Mass Atrocities by State Forces', 'Massacre'),
('State Violence Against Civilians', 'Forced Displacement by State', 'Forced Relocation')
ON CONFLICT DO NOTHING;

-- Insert common African locations
INSERT INTO locations (country, city, region, location_type) VALUES
('Nigeria', 'Maiduguri', 'Borno State', 'City'),
('Nigeria', 'Abuja', 'Federal Capital Territory', 'City'),
('Nigeria', 'Lagos', 'Lagos State', 'City'),
('Somalia', 'Mogadishu', 'Banaadir', 'City'),
('Somalia', 'Kismayo', 'Lower Juba', 'City'),
('Sudan', 'Khartoum', 'Khartoum State', 'City'),
('Sudan', 'Darfur', 'Darfur Region', 'Region'),
('South Sudan', 'Juba', 'Central Equatoria', 'City'),
('Kenya', 'Nairobi', 'Nairobi County', 'City'),
('Kenya', 'Mombasa', 'Mombasa County', 'City'),
('Ethiopia', 'Addis Ababa', 'Addis Ababa', 'City'),
('Mali', 'Bamako', 'Bamako Region', 'City'),
('Burkina Faso', 'Ouagadougou', 'Centre Region', 'City'),
('Niger', 'Niamey', 'Niamey', 'City'),
('Cameroon', 'Yaoundé', 'Centre Region', 'City')
ON CONFLICT DO NOTHING;

-- Insert common armed groups
INSERT INTO actors (actor_name, actor_type, actor_category, country) VALUES
('Boko Haram', 'Non-state armed group', 'Islamist Insurgency', 'Nigeria'),
('Al-Shabaab', 'Non-state armed group', 'Islamist Insurgency', 'Somalia'),
('ISWAP', 'Non-state armed group', 'Islamist Insurgency', 'Nigeria'),
('Rapid Support Forces', 'Non-state armed group', 'Paramilitary', 'Sudan'),
('Allied Democratic Forces', 'Non-state armed group', 'Rebel Group', 'Uganda'),
('Lord''s Resistance Army', 'Non-state armed group', 'Rebel Group', 'Uganda'),
('Jama''at Nasr al-Islam wal Muslimin', 'Non-state armed group', 'Islamist Insurgency', 'Mali'),
('Civilian', 'Victim category', 'Non-combatant', NULL),
('Government forces', 'State actor', 'Military', NULL),
('Police', 'State actor', 'Law Enforcement', NULL)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- ML/EXTRACTION TRACKING TABLES
-- ============================================================================

-- History Table (Track NER extractions for analytics)
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    text_hash VARCHAR(64),
    entities_json JSON,
    structured_event_json JSON,
    confidence_scores_json JSON,
    entity_count INTEGER DEFAULT 0,
    processing_time_ms FLOAT,
    model_version VARCHAR(50),
    user_rating INTEGER,
    user_feedback TEXT,
    corrections_json JSON,
    saved_to_events BOOLEAN DEFAULT FALSE,
    event_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_request ON history(request_id);
CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at);
CREATE INDEX IF NOT EXISTS idx_history_hash ON history(text_hash);

-- Trainings Table (Track ML training sessions)
CREATE TABLE IF NOT EXISTS trainings (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    model_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    epochs_total INTEGER,
    epochs_completed INTEGER DEFAULT 0,
    best_epoch INTEGER,
    best_val_loss FLOAT,
    best_val_accuracy FLOAT,
    train_samples INTEGER,
    val_samples INTEGER,
    batch_size INTEGER,
    learning_rate FLOAT,
    max_sequence_length INTEGER,
    checkpoint_path TEXT,
    train_data_path TEXT,
    val_data_path TEXT,
    config_json JSON,
    metrics_history_json JSON,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    is_active BOOLEAN DEFAULT FALSE
);

-- Ensure only one training can be active at a time
CREATE UNIQUE INDEX IF NOT EXISTS idx_trainings_single_active
ON trainings (is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_trainings_session ON trainings(session_id);
CREATE INDEX IF NOT EXISTS idx_trainings_status ON trainings(status);
CREATE INDEX IF NOT EXISTS idx_trainings_started ON trainings(started_at);

-- ============================================================================
-- PERFORMANCE TUNING
-- ============================================================================

-- Analyze tables for query optimization
VACUUM ANALYZE events;
VACUUM ANALYZE actors;
VACUUM ANALYZE locations;
VACUUM ANALYZE taxonomies;

-- ============================================================================
-- PERMISSIONS (Adjust based on your security requirements)
-- ============================================================================

-- Create read-only role for analysts
-- CREATE ROLE event_analyst;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO event_analyst;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO event_analyst;

-- Create read-write role for pipeline
-- CREATE ROLE event_pipeline;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO event_pipeline;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO event_pipeline;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Week 7-8 Event Database Schema Created';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database is ready to receive events from Week 3-6 NLP Pipeline';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run: python3 pipeline_connector.py --test';
    RAISE NOTICE '  2. Import events: python3 import_events.py --csv <file>';
    RAISE NOTICE '  3. Start API: python3 api_server.py';
    RAISE NOTICE '========================================';
END $$;

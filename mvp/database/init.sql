-- Garmin Longevity Matrix MVP Database Schema
-- Simplified for production deployment

-- Create garmin schema
CREATE SCHEMA IF NOT EXISTS garmin;

-- Staging table for raw activities
CREATE TABLE IF NOT EXISTS garmin.staging_activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT UNIQUE,
    activity_type VARCHAR(50),
    activity_name VARCHAR(255),
    start_time TIMESTAMP,
    duration_seconds INTEGER,
    distance_meters NUMERIC(10,2),
    calories INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_speed NUMERIC(10,3),
    elevation_gain NUMERIC(10,2),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for heart rate data
CREATE TABLE IF NOT EXISTS garmin.staging_heart_rate (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    resting_heart_rate INTEGER,
    min_heart_rate INTEGER,
    max_heart_rate INTEGER,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for sleep data
CREATE TABLE IF NOT EXISTS garmin.staging_sleep (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    total_sleep_seconds INTEGER,
    deep_sleep_seconds INTEGER,
    light_sleep_seconds INTEGER,
    rem_sleep_seconds INTEGER,
    sleep_score INTEGER,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for daily stats
CREATE TABLE IF NOT EXISTS garmin.staging_daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    total_steps INTEGER,
    total_distance_meters NUMERIC(10,2),
    total_calories INTEGER,
    active_calories INTEGER,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processed daily metrics table
CREATE TABLE IF NOT EXISTS garmin.processed_daily_metrics (
    date DATE PRIMARY KEY,
    total_steps INTEGER,
    total_calories INTEGER,
    active_calories INTEGER,
    resting_heart_rate INTEGER,
    max_heart_rate INTEGER,
    activities_count INTEGER,
    total_distance_km NUMERIC(10,2),
    total_activity_duration_minutes INTEGER,
    biological_age NUMERIC(5,2),
    longevity_score INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health insights table
CREATE TABLE IF NOT EXISTS garmin.health_insights (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    biological_age NUMERIC(5,2),
    aging_velocity NUMERIC(5,3),
    longevity_score INTEGER,
    activity_consistency INTEGER,
    recovery_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User settings table for MVP
CREATE TABLE IF NOT EXISTS garmin.user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER DEFAULT 1, -- Single user for MVP
    garmin_email VARCHAR(255),
    sync_enabled BOOLEAN DEFAULT true,
    sync_frequency VARCHAR(20) DEFAULT 'daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_activities_date ON garmin.staging_activities(DATE(start_time));
CREATE INDEX IF NOT EXISTS idx_activities_type ON garmin.staging_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_heart_rate_date ON garmin.staging_heart_rate(date);
CREATE INDEX IF NOT EXISTS idx_sleep_date ON garmin.staging_sleep(date);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON garmin.staging_daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_processed_date ON garmin.processed_daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_insights_date ON garmin.health_insights(date);

-- Insert default user settings
INSERT INTO garmin.user_settings (user_id, sync_enabled) 
VALUES (1, true) 
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Garmin Longevity Matrix MVP database initialized successfully!';
END $$;
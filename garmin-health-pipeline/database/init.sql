-- database/init.sql
-- PostgreSQL schema for Garmin health data pipeline

-- Create schema
CREATE SCHEMA IF NOT EXISTS garmin;

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- STAGING TABLES (for raw extracted data)
-- =====================================================

-- Staging table for activities
CREATE TABLE IF NOT EXISTS garmin.staging_activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT UNIQUE,
    activity_type VARCHAR(50),
    activity_name VARCHAR(255),
    start_time TIMESTAMP,
    duration_seconds INTEGER,
    distance_meters DECIMAL(10, 2),
    calories INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_speed DECIMAL(10, 3),
    max_speed DECIMAL(10, 3),
    elevation_gain DECIMAL(10, 2),
    elevation_loss DECIMAL(10, 2),
    avg_cadence INTEGER,
    training_effect VARCHAR(50),
    aerobic_effect DECIMAL(3, 1),
    anaerobic_effect DECIMAL(3, 1),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for heart rate data
CREATE TABLE IF NOT EXISTS garmin.staging_heart_rate (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    resting_heart_rate INTEGER,
    min_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_heart_rate DECIMAL(5, 2),
    heart_rate_zones JSONB,
    time_series JSONB,
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
    awake_seconds INTEGER,
    sleep_start_time TIMESTAMP,
    sleep_end_time TIMESTAMP,
    sleep_quality VARCHAR(50),
    sleep_score INTEGER,
    avg_respiration DECIMAL(5, 2),
    avg_spo2 DECIMAL(5, 2),
    sleep_movement JSONB,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for stress data
CREATE TABLE IF NOT EXISTS garmin.staging_stress (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    avg_stress_level INTEGER,
    max_stress_level INTEGER,
    stress_duration_seconds INTEGER,
    rest_stress_duration INTEGER,
    activity_stress_duration INTEGER,
    low_stress_duration INTEGER,
    medium_stress_duration INTEGER,
    high_stress_duration INTEGER,
    stress_values JSONB,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for body composition
CREATE TABLE IF NOT EXISTS garmin.staging_body_composition (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    weight_kg DECIMAL(5, 2),
    bmi DECIMAL(5, 2),
    body_fat_percentage DECIMAL(5, 2),
    muscle_mass_kg DECIMAL(5, 2),
    bone_mass_kg DECIMAL(5, 2),
    body_water_percentage DECIMAL(5, 2),
    metabolic_age INTEGER,
    visceral_fat INTEGER,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging table for daily summary
CREATE TABLE IF NOT EXISTS garmin.staging_daily_summary (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    total_steps INTEGER,
    total_distance_meters DECIMAL(10, 2),
    highly_active_seconds INTEGER,
    active_seconds INTEGER,
    sedentary_seconds INTEGER,
    sleeping_seconds INTEGER,
    total_calories INTEGER,
    active_calories INTEGER,
    bmr_calories INTEGER,
    floors_climbed INTEGER,
    floors_descended INTEGER,
    intensity_minutes_goal INTEGER,
    intensity_minutes INTEGER,
    vigorous_intensity_minutes INTEGER,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PROCESSED TABLES (cleaned and transformed data)
-- =====================================================

-- Main activities table
CREATE TABLE IF NOT EXISTS garmin.activities (
    activity_id BIGINT PRIMARY KEY,
    activity_type VARCHAR(50),
    activity_name VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes DECIMAL(10, 2),
    distance_km DECIMAL(10, 3),
    pace_min_per_km DECIMAL(5, 2),
    speed_kmh DECIMAL(5, 2),
    calories INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    heart_rate_zones JSONB,
    elevation_gain_m DECIMAL(10, 2),
    elevation_loss_m DECIMAL(10, 2),
    avg_cadence INTEGER,
    training_effect VARCHAR(50),
    aerobic_effect DECIMAL(3, 1),
    anaerobic_effect DECIMAL(3, 1),
    training_load INTEGER,
    recovery_time_hours INTEGER,
    vo2_max DECIMAL(5, 2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily metrics table
CREATE TABLE IF NOT EXISTS garmin.daily_metrics (
    date DATE PRIMARY KEY,
    -- Heart Rate
    resting_heart_rate INTEGER,
    avg_heart_rate DECIMAL(5, 2),
    max_heart_rate INTEGER,
    min_heart_rate INTEGER,
    hrv_score INTEGER,
    -- Sleep
    sleep_duration_hours DECIMAL(4, 2),
    deep_sleep_hours DECIMAL(4, 2),
    light_sleep_hours DECIMAL(4, 2),
    rem_sleep_hours DECIMAL(4, 2),
    sleep_efficiency DECIMAL(5, 2),
    sleep_score INTEGER,
    -- Stress
    avg_stress_level INTEGER,
    max_stress_level INTEGER,
    low_stress_percentage DECIMAL(5, 2),
    medium_stress_percentage DECIMAL(5, 2),
    high_stress_percentage DECIMAL(5, 2),
    -- Activity
    total_steps INTEGER,
    distance_km DECIMAL(10, 3),
    floors_climbed INTEGER,
    active_minutes INTEGER,
    intensity_minutes INTEGER,
    sedentary_minutes INTEGER,
    -- Calories
    total_calories INTEGER,
    active_calories INTEGER,
    bmr_calories INTEGER,
    -- Body Metrics
    weight_kg DECIMAL(5, 2),
    bmi DECIMAL(5, 2),
    body_fat_percentage DECIMAL(5, 2),
    muscle_mass_kg DECIMAL(5, 2),
    -- Performance
    body_battery INTEGER,
    training_readiness INTEGER,
    recovery_time_hours INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly aggregated metrics
CREATE TABLE IF NOT EXISTS garmin.weekly_metrics (
    week_start DATE PRIMARY KEY,
    week_end DATE,
    -- Activity Summary
    total_activities INTEGER,
    total_distance_km DECIMAL(10, 2),
    total_duration_hours DECIMAL(10, 2),
    total_calories INTEGER,
    avg_training_load DECIMAL(10, 2),
    -- Sleep Summary
    avg_sleep_hours DECIMAL(4, 2),
    avg_sleep_score DECIMAL(5, 2),
    total_deep_sleep_hours DECIMAL(5, 2),
    total_rem_sleep_hours DECIMAL(5, 2),
    -- Heart Rate Summary
    avg_resting_hr INTEGER,
    avg_daily_hr DECIMAL(5, 2),
    -- Stress Summary
    avg_stress_level DECIMAL(5, 2),
    high_stress_hours DECIMAL(10, 2),
    -- Steps and Movement
    total_steps INTEGER,
    avg_daily_steps INTEGER,
    total_floors INTEGER,
    -- Performance Trends
    vo2_max_trend DECIMAL(5, 2),
    fitness_age INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monthly aggregated metrics
CREATE TABLE IF NOT EXISTS garmin.monthly_metrics (
    month_start DATE PRIMARY KEY,
    month_end DATE,
    year INTEGER,
    month INTEGER,
    -- Activity Statistics
    total_activities INTEGER,
    total_distance_km DECIMAL(10, 2),
    total_duration_hours DECIMAL(10, 2),
    total_calories INTEGER,
    most_frequent_activity VARCHAR(50),
    longest_activity_minutes DECIMAL(10, 2),
    -- Sleep Statistics
    avg_sleep_hours DECIMAL(4, 2),
    best_sleep_score INTEGER,
    worst_sleep_score INTEGER,
    sleep_consistency_score DECIMAL(5, 2),
    -- Health Trends
    avg_resting_hr INTEGER,
    weight_change_kg DECIMAL(5, 2),
    body_fat_change_percentage DECIMAL(5, 2),
    -- Goals Achievement
    step_goal_achievement_rate DECIMAL(5, 2),
    intensity_minutes_achievement_rate DECIMAL(5, 2),
    -- Performance
    avg_vo2_max DECIMAL(5, 2),
    training_load_balance VARCHAR(20),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personal records table
CREATE TABLE IF NOT EXISTS garmin.personal_records (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    activity_type VARCHAR(50),
    record_type VARCHAR(50), -- 'distance', 'time', 'pace', 'heart_rate', etc.
    record_value DECIMAL(15, 3),
    record_unit VARCHAR(20),
    activity_id BIGINT REFERENCES garmin.activities(activity_id),
    achieved_date DATE,
    previous_value DECIMAL(15, 3),
    improvement_percentage DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Goals and targets table
CREATE TABLE IF NOT EXISTS garmin.goals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    goal_type VARCHAR(50), -- 'daily_steps', 'weekly_distance', 'weight_loss', etc.
    target_value DECIMAL(15, 3),
    target_unit VARCHAR(20),
    start_date DATE,
    end_date DATE,
    current_value DECIMAL(15, 3),
    completion_percentage DECIMAL(5, 2),
    status VARCHAR(20), -- 'active', 'completed', 'failed', 'paused'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training plans table
CREATE TABLE IF NOT EXISTS garmin.training_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    plan_name VARCHAR(255),
    plan_type VARCHAR(50), -- 'marathon', '5k', 'cycling', etc.
    start_date DATE,
    end_date DATE,
    target_event VARCHAR(255),
    current_week INTEGER,
    total_weeks INTEGER,
    adherence_rate DECIMAL(5, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Activities indexes
CREATE INDEX idx_activities_start_time ON garmin.activities(start_time DESC);
CREATE INDEX idx_activities_type ON garmin.activities(activity_type);
CREATE INDEX idx_activities_training_effect ON garmin.activities(training_effect);

-- Daily metrics indexes
CREATE INDEX idx_daily_metrics_date ON garmin.daily_metrics(date DESC);
CREATE INDEX idx_daily_metrics_sleep_score ON garmin.daily_metrics(sleep_score);
CREATE INDEX idx_daily_metrics_stress ON garmin.daily_metrics(avg_stress_level);

-- Weekly metrics indexes
CREATE INDEX idx_weekly_metrics_week ON garmin.weekly_metrics(week_start DESC);

-- Monthly metrics indexes
CREATE INDEX idx_monthly_metrics_month ON garmin.monthly_metrics(month_start DESC);
CREATE INDEX idx_monthly_metrics_year ON garmin.monthly_metrics(year, month);

-- Personal records indexes
CREATE INDEX idx_personal_records_type ON garmin.personal_records(activity_type, record_type);
CREATE INDEX idx_personal_records_date ON garmin.personal_records(achieved_date DESC);

-- Goals indexes
CREATE INDEX idx_goals_status ON garmin.goals(status);
CREATE INDEX idx_goals_dates ON garmin.goals(start_date, end_date);

-- =====================================================
-- VIEWS FOR DASHBOARD
-- =====================================================

-- Current week overview
CREATE OR REPLACE VIEW garmin.v_current_week_overview AS
SELECT 
    DATE_TRUNC('week', CURRENT_DATE) as week_start,
    COUNT(DISTINCT a.activity_id) as total_activities,
    COALESCE(SUM(a.distance_km), 0) as total_distance,
    COALESCE(SUM(a.duration_minutes), 0) as total_duration,
    COALESCE(AVG(dm.sleep_duration_hours), 0) as avg_sleep,
    COALESCE(AVG(dm.avg_stress_level), 0) as avg_stress,
    COALESCE(SUM(dm.total_steps), 0) as total_steps,
    COALESCE(AVG(dm.resting_heart_rate), 0) as avg_resting_hr
FROM garmin.daily_metrics dm
LEFT JOIN garmin.activities a ON DATE(a.start_time) = dm.date
WHERE dm.date >= DATE_TRUNC('week', CURRENT_DATE)
    AND dm.date < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '7 days'
GROUP BY week_start;

-- Training load balance view
CREATE OR REPLACE VIEW garmin.v_training_load_balance AS
WITH recent_load AS (
    SELECT 
        DATE(start_time) as activity_date,
        SUM(training_load) as daily_load
    FROM garmin.activities
    WHERE start_time >= CURRENT_DATE - INTERVAL '42 days'
    GROUP BY DATE(start_time)
),
load_metrics AS (
    SELECT 
        AVG(CASE WHEN activity_date >= CURRENT_DATE - INTERVAL '7 days' 
            THEN daily_load END) as acute_load,
        AVG(CASE WHEN activity_date >= CURRENT_DATE - INTERVAL '28 days' 
            THEN daily_load END) as chronic_load
    FROM recent_load
)
SELECT 
    acute_load,
    chronic_load,
    CASE 
        WHEN chronic_load > 0 THEN acute_load / chronic_load 
        ELSE 0 
    END as training_stress_balance,
    CASE 
        WHEN chronic_load = 0 THEN 'No Training'
        WHEN acute_load / NULLIF(chronic_load, 0) < 0.8 THEN 'Detraining'
        WHEN acute_load / NULLIF(chronic_load, 0) BETWEEN 0.8 AND 1.3 THEN 'Optimal'
        WHEN acute_load / NULLIF(chronic_load, 0) BETWEEN 1.3 AND 1.5 THEN 'Overreaching'
        ELSE 'Overtraining Risk'
    END as load_status
FROM load_metrics;

-- Sleep quality trend view
CREATE OR REPLACE VIEW garmin.v_sleep_quality_trend AS
SELECT 
    date,
    sleep_score,
    sleep_duration_hours,
    deep_sleep_hours,
    rem_sleep_hours,
    sleep_efficiency,
    AVG(sleep_score) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_avg_score,
    AVG(sleep_duration_hours) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_avg_duration
FROM garmin.daily_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION garmin.update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON garmin.activities
    FOR EACH ROW EXECUTE FUNCTION garmin.update_updated_at_column();

CREATE TRIGGER update_daily_metrics_updated_at BEFORE UPDATE ON garmin.daily_metrics
    FOR EACH ROW EXECUTE FUNCTION garmin.update_updated_at_column();

CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON garmin.goals
    FOR EACH ROW EXECUTE FUNCTION garmin.update_updated_at_column();

-- Function to calculate training zones
CREATE OR REPLACE FUNCTION garmin.calculate_heart_rate_zones(
    max_hr INTEGER,
    resting_hr INTEGER
) RETURNS JSONB AS $
DECLARE
    zones JSONB;
    hr_reserve INTEGER;
BEGIN
    hr_reserve := max_hr - resting_hr;
    
    zones := jsonb_build_object(
        'zone1', jsonb_build_object(
            'name', 'Recovery',
            'min', resting_hr + (hr_reserve * 0.5),
            'max', resting_hr + (hr_reserve * 0.6)
        ),
        'zone2', jsonb_build_object(
            'name', 'Base',
            'min', resting_hr + (hr_reserve * 0.6),
            'max', resting_hr + (hr_reserve * 0.7)
        ),
        'zone3', jsonb_build_object(
            'name', 'Tempo',
            'min', resting_hr + (hr_reserve * 0.7),
            'max', resting_hr + (hr_reserve * 0.8)
        ),
        'zone4', jsonb_build_object(
            'name', 'Threshold',
            'min', resting_hr + (hr_reserve * 0.8),
            'max', resting_hr + (hr_reserve * 0.9)
        ),
        'zone5', jsonb_build_object(
            'name', 'VO2 Max',
            'min', resting_hr + (hr_reserve * 0.9),
            'max', max_hr
        )
    );
    
    RETURN zones;
END;
$ LANGUAGE plpgsql;

-- =====================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- =====================================================

-- Activity summary by type
CREATE MATERIALIZED VIEW garmin.mv_activity_summary_by_type AS
SELECT 
    activity_type,
    COUNT(*) as activity_count,
    SUM(distance_km) as total_distance,
    SUM(duration_minutes) as total_duration,
    AVG(pace_min_per_km) as avg_pace,
    AVG(avg_heart_rate) as avg_heart_rate,
    SUM(calories) as total_calories,
    MAX(distance_km) as longest_distance,
    MAX(duration_minutes) as longest_duration,
    MIN(pace_min_per_km) as best_pace
FROM garmin.activities
WHERE start_time >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY activity_type;

-- Create index on materialized view
CREATE INDEX idx_mv_activity_type ON garmin.mv_activity_summary_by_type(activity_type);

-- Refresh function for materialized views
CREATE OR REPLACE FUNCTION garmin.refresh_materialized_views()
RETURNS void AS $
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY garmin.mv_activity_summary_by_type;
END;
$ LANGUAGE plpgsql;

-- =====================================================
-- DATA QUALITY CHECKS
-- =====================================================

-- Table for data quality metrics
CREATE TABLE IF NOT EXISTS garmin.data_quality_checks (
    id SERIAL PRIMARY KEY,
    check_date DATE,
    check_type VARCHAR(50),
    table_name VARCHAR(100),
    total_records INTEGER,
    null_count INTEGER,
    duplicate_count INTEGER,
    anomaly_count INTEGER,
    quality_score DECIMAL(5, 2),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to check data quality
CREATE OR REPLACE FUNCTION garmin.check_data_quality(
    p_table_name TEXT,
    p_date DATE DEFAULT CURRENT_DATE
) RETURNS void AS $
DECLARE
    v_total_records INTEGER;
    v_null_count INTEGER;
    v_quality_score DECIMAL(5, 2);
BEGIN
    -- Get total records
    EXECUTE format('SELECT COUNT(*) FROM garmin.%I WHERE date = $1', p_table_name)
    INTO v_total_records
    USING p_date;
    
    -- Calculate quality score (simplified)
    v_quality_score := CASE 
        WHEN v_total_records > 0 THEN 100.0
        ELSE 0.0
    END;
    
    -- Insert quality check result
    INSERT INTO garmin.data_quality_checks (
        check_date,
        check_type,
        table_name,
        total_records,
        quality_score
    ) VALUES (
        p_date,
        'daily_check',
        p_table_name,
        v_total_records,
        v_quality_score
    );
END;
$ LANGUAGE plpgsql;

-- =====================================================
-- PERMISSIONS
-- =====================================================

-- Create read-only role for dashboard
CREATE ROLE garmin_dashboard_read;
GRANT USAGE ON SCHEMA garmin TO garmin_dashboard_read;
GRANT SELECT ON ALL TABLES IN SCHEMA garmin TO garmin_dashboard_read;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA garmin TO garmin_dashboard_read;

-- Create write role for ETL processes
CREATE ROLE garmin_etl_write;
GRANT USAGE ON SCHEMA garmin TO garmin_etl_write;
GRANT ALL ON ALL TABLES IN SCHEMA garmin TO garmin_etl_write;
GRANT ALL ON ALL SEQUENCES IN SCHEMA garmin TO garmin_etl_write;

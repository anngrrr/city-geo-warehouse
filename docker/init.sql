CREATE DATABASE city_metrics;

\connect city_metrics;

CREATE SCHEMA IF NOT EXISTS city_data;

CREATE TYPE IF NOT EXISTS data_source_status AS ENUM ('success', 'partial', 'failed');

CREATE TABLE IF NOT EXISTS city_data.city_metrics (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    population INTEGER CHECK (population >= 0),
    latitude DOUBLE PRECISION CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION CHECK (longitude BETWEEN -180 AND 180),
    region VARCHAR(255),
    elevation DOUBLE PRECISION,
    timezone VARCHAR(100),
    happiness_index DOUBLE PRECISION CHECK (happiness_index BETWEEN 0 AND 100),
    health_index DOUBLE PRECISION CHECK (health_index BETWEEN 0 AND 100),
    cost_of_living_index DOUBLE PRECISION CHECK (cost_of_living_index BETWEEN 0 AND 100),
    housing_price_index DOUBLE PRECISION CHECK (housing_price_index BETWEEN 0 AND 100),
    traffic_congestion_score DOUBLE PRECISION CHECK (traffic_congestion_score BETWEEN 0 AND 100),
    education_level_score DOUBLE PRECISION CHECK (education_level_score BETWEEN 0 AND 100),
    cultural_events_per_capita DOUBLE PRECISION CHECK (cultural_events_per_capita BETWEEN 0 AND 100),
    sports_facilities_per_capita DOUBLE PRECISION CHECK (sports_facilities_per_capita BETWEEN 0 AND 100),
    economic_growth_rate DOUBLE PRECISION,
    average_salary DOUBLE PRECISION CHECK (average_salary >= 0),
    rent_price_index DOUBLE PRECISION CHECK (rent_price_index >= 0),
    wind_speed_avg DOUBLE PRECISION CHECK (wind_speed_avg >= 0),
    air_quality_index DOUBLE PRECISION CHECK (air_quality_index >= 0),
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION CHECK (humidity BETWEEN 0 AND 100),
    distance_to_water DOUBLE PRECISION CHECK (distance_to_water >= 0),
    distance_to_mountains DOUBLE PRECISION CHECK (distance_to_mountains >= 0),
    distance_to_forest DOUBLE PRECISION CHECK (distance_to_forest >= 0),
    distance_to_park DOUBLE PRECISION CHECK (distance_to_park >= 0),
    forest_proximity_score DOUBLE PRECISION CHECK (forest_proximity_score BETWEEN 0 AND 100),
    green_space_ratio DOUBLE PRECISION CHECK (green_space_ratio BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_city_country_timestamp UNIQUE (city_name, country, timestamp)
);

CREATE TABLE IF NOT EXISTS city_data.data_updates (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,
    status data_source_status NOT NULL,
    error_message TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_city_country ON city_data.city_metrics (city_name, country);
CREATE INDEX IF NOT EXISTS idx_timestamp ON city_data.city_metrics (timestamp);
CREATE INDEX IF NOT EXISTS idx_updates_status ON city_data.data_updates (status);

CREATE OR REPLACE FUNCTION city_data.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_city_metrics_updated_at ON city_data.city_metrics;
CREATE TRIGGER update_city_metrics_updated_at
    BEFORE UPDATE ON city_data.city_metrics
    FOR EACH ROW
    EXECUTE FUNCTION city_data.update_updated_at_column();

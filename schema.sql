-- Create the database
CREATE DATABASE IF NOT EXISTS urban_mobility;
USE urban_mobility;

-- Create the trips table
CREATE TABLE IF NOT EXISTS trips (
    trip_id VARCHAR(50) PRIMARY KEY,
    vendor_id INT NOT NULL,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count INT NOT NULL,
    pickup_longitude DOUBLE NOT NULL,
    pickup_latitude DOUBLE NOT NULL,
    dropoff_longitude DOUBLE NOT NULL,
    dropoff_latitude DOUBLE NOT NULL,
    store_and_fwd_flag CHAR(1),
    trip_duration INT NOT NULL,
    pickup_time TIME NOT NULL,
    pickup_day_of_week VARCHAR(10) NOT NULL,
    pickup_month VARCHAR(10) NOT NULL,
    trip_distance_km FLOAT NOT NULL,
    trip_speed_kmh FLOAT NOT NULL,
    trip_distance_category VARCHAR(10) NOT NULL
);

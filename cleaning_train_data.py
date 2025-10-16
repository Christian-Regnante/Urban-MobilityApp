import pandas as pd
import numpy as np
from math import radians, sin, cos, asin, sqrt
import zipfile
import os

def clean_data():
    zip_file_path = "train.zip"
    extract_dir = "."

    if not os.path.exists("train.csv"):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"{zip_file_path} was extracted successfully\n")

    df = pd.read_csv("train.csv")

    # Invalid coordinates
    invalid_coords = df[
        (df['pickup_latitude'] < -90) | (df['pickup_latitude'] > 90) |
        (df['dropoff_latitude'] < -90) | (df['dropoff_latitude'] > 90) |
        (df['pickup_longitude'] < -180) | (df['pickup_longitude'] > 180) |
        (df['dropoff_longitude'] < -180) | (df['dropoff_longitude'] > 180)
    ]

    # Invalid duration or passengers
    invalid_duration = df[df['trip_duration'] <= 0]
    invalid_passengers = df[(df['passenger_count'] == 0) | (df['passenger_count'] > 6)]

    excluded = pd.concat([invalid_coords, invalid_duration, invalid_passengers]).drop_duplicates()
    excluded.to_csv("excluded_records.log", index=False)
    df = df[~df['id'].isin(excluded['id'])]

    print(f"Excluded {len(excluded)} invalid records. Remaining: {len(df)}")

    # Convert to datetime
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    # Derived time features
    df['pickup_day_of_week'] = df['pickup_datetime'].dt.day_name()
    df['pickup_month'] = df['pickup_datetime'].dt.month_name()

    # Distance using Haversine
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c

    df['trip_distance_km'] = df.apply(lambda r: haversine(
        r['pickup_longitude'], r['pickup_latitude'],
        r['dropoff_longitude'], r['dropoff_latitude']), axis=1)

    df['trip_speed_kmh'] = df['trip_distance_km'] / (df['trip_duration'] / 3600)
    df['trip_speed_kmh'] = df['trip_speed_kmh'].replace([np.inf, -np.inf], np.nan)

    df.dropna(subset=['trip_distance_km', 'trip_speed_kmh'], inplace=True)
    df.drop_duplicates(inplace=True)

    df.to_csv('cleaned_trips.csv', index=False)
    print("✅ Cleaning complete. Saved as cleaned_trips.csv")

    return df

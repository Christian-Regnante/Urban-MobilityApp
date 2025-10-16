import pandas as pd
import numpy as np
from math import radians, sin, cos, asin, sqrt
import zipfile
import os

# Path to your zip file
zip_file_path = "train.zip"

# Directory where you want to extract files
extract_dir = "."

# Create the directory if it doesn't exist
os.makedirs(extract_dir, exist_ok=True)

# Open the zip file and extract all contents
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"{zip_file_path} was extracted successfully\n")


#------------------------------------------------------- STEP 1: Load and Explore the Dataset
# Load the dataset
df = pd.read_csv("train.csv")

# # Display the basic info
# print(df.info())
# print()
# print("\n--- Preview ---")
# print(df.head())

# # Basic statistics
# print("\n--- Basic Description ---")
# print(df.describe())

# # Check for missing values
# print("\n--- Missing Values ---")
# print(df.isnull().sum())

pd.set_option('display.max_columns', None)     # show all columns
pd.set_option('display.width', 2000)           # wide output so it doesn't wrap
pd.set_option('display.max_colwidth', None)    # show full column content

#------------------------------------------------------- STEP 2: Detect and Handle Outliers or Invalid Data

# 1. Invalid coordinates
invalid_coords = df[
    (df['pickup_latitude'] < -90) | (df['pickup_latitude'] > 90) |
    (df['dropoff_latitude'] < -90) | (df['dropoff_latitude'] > 90) |
    (df['pickup_longitude'] < -180) | (df['pickup_longitude'] > 180) |
    (df['dropoff_longitude'] < -180) | (df['dropoff_longitude'] > 180)
]

# 2. Invalid trip duration (<= 0)
invalid_duration = df[df['trip_duration'] <= 0]

# 3. Unusual passenger counts (0 or > 6)
invalid_passengers = df[(df['passenger_count'] == 0) | (df['passenger_count'] > 6)]

# Combine and log excluded records
excluded = pd.concat([invalid_coords, invalid_duration, invalid_passengers]).drop_duplicates()
excluded.to_csv("excluded_records.log", index=False)

# Remove them from the main dataframe
df = df[~df['id'].isin(excluded['id'])]

print(f"Excluded {len(excluded)} invalid records. Remaining records: {len(df)}\n\n")
# print(df.info())

#------------------------------------------------------- STEP 3: Convert Datatypes and Create Useful Time Features

# Convert to datetime
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

# Derived features
df['pickup_time'] = df['pickup_datetime'].dt.strftime('%H:%M:%S')
# df['pickup_hour'] = df['pickup_datetime'].dt.hour
df['pickup_day_of_week'] = df['pickup_datetime'].dt.day_name()
df['pickup_month'] = df['pickup_datetime'].dt.month_name()

# print(df.head(2))

#------------------------------------------------------- STEP 4: Calculate Distance Between Pickup and Dropoff


def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

df['trip_distance_km'] = df.apply(lambda row: haversine(
    row['pickup_longitude'], row['pickup_latitude'],
    row['dropoff_longitude'], row['dropoff_latitude']), axis=1)


#------------------------------------------------------- STEP 5: Add More Derived Features

# Trip speed in km/h
df['trip_speed_kmh'] = df['trip_distance_km'] / (df['trip_duration'] / 3600)
df['trip_speed_kmh'] = df['trip_speed_kmh'].replace([np.inf, -np.inf], np.nan)

# Trip distance category
def categorize_distance(d):
    if d < 2:
        return 'short'
    elif d < 5:
        return 'medium'
    else:
        return 'long'

df['trip_distance_category'] = df['trip_distance_km'].apply(categorize_distance)

# print(df[['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude', 'trip_distance_km']].head(5))

# print(df[['trip_duration', 'trip_distance_km', 'trip_speed_kmh', 'trip_distance_category']].head(5))

#------------------------------------------------------- STEP 6: Final Cleaning and Save

# Drop NaN in critical fields
df = df.dropna(subset=['trip_distance_km', 'trip_speed_kmh'])

# Remove duplicates (if any)
df = df.drop_duplicates()

print(df.info())
print()
print(df.head(5))

# Save cleaned data
df.to_csv('cleaned_trips.csv', index=False)

print("\n✅ Cleaning complete! Cleaned data saved as 'cleaned_trips.csv'\n")

#------------------------------------------------------- Bonus: Summary of cleaning

summary = {
    "original_records": 1458644,
    "excluded_records": len(excluded),
    "final_records": len(df),
    "derived_features": ["pickup_hour", "pickup_day_of_week", "trip_speed_kmh", "trip_distance_category"]
}

print("Cleaning Summary:", summary)

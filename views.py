from flask import Blueprint, jsonify, render_template, request
# import MySQLdb
from connection import connection


# Check if connection was successful
if connection:
    print("Connection to the database was successful")
else:
    print("Connection to MySQL DB failed")
    exit(1)


# Create blueprints
home = Blueprint('home', __name__)
api = Blueprint('api', __name__)


# Home routes
@home.route('/')
def index():
    # return "Welcome to the Urban Mobility App!"
    return render_template('index.html')


# API routes
@api.route('/')
def api_home():
    return "Welcome to the Urban Mobility App REST APIs!"

# Fetching all trips
@api.route('/trips', methods=['GET'])
def get_data():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM trips LIMIT 10")
    rows = cursor.fetchall()
    cursor.close()

     # Converting fetched data to a list of dictionaries for better JSON representation

    trips = []
    for row in rows:
        trips.append({
            'trip_id': row[0],
            'vendor_id': row[1],
            'pickup_datetime': str(row[2]),
            'dropoff_datetime': str(row[3]),
            'passenger_count': row[4],
            'pickup_longitude': row[5],
            'pickup_latitude': row[6],
            'dropoff_longitude': row[7],
            'dropoff_latitude': row[8],
            'store_and_fwd_flag': row[9],
            'trip_duration': row[10],
            'pickup_time': str(row[11]),
            'pickup_day_of_week': row[12],
            'pickup_month': row[13],
            'trip_distance_km': row[14],
            'trip_speed_kmh': row[15],
            'trip_distance_category': row[16]
        })

    return jsonify(trips)
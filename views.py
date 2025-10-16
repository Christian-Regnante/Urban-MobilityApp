from flask import Blueprint, jsonify, render_template, request
from connection import connection
from algorithms import quicksort_trips


# Check if connection was successful
if connection:
    print("Connection to the database was successful")
else:
    print("Connection to MySQL DB failed")
    exit(1)


# Create blueprints
home = Blueprint('home', __name__)
api = Blueprint('api', __name__, template_folder="/templates", static_folder="/static")


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
    cursor.execute("SELECT * FROM trips LIMIT 10000")
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

# API route: Filter trips
@api.route('/trips/filter', methods=['GET'])
def filter_trips():
    vendor = request.args.get('vendor_id')
    passengers = request.args.get('passenger_count')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # cursor = connection.cursor(dictionary=True)
    cursor = connection.cursor()

    query = "SELECT * FROM trips LIMIT 1000 WHERE 1=1"
    params = []

    if vendor:
        query += " AND vendor_id = %s"
        params.append(vendor)
    if passengers:
        query += " AND passenger_count = %s"
        params.append(passengers)
    if start_date and end_date:
        query += " AND pickup_datetime BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)

# API route: Average speed by hour
@api.route('/api/insights/average_speed', methods=['GET'])
def average_speed():
    # cursor = connection.cursor(dictionary=True)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT HOUR(pickup_datetime) AS hour, 
               ROUND(AVG(trip_speed_kmh), 2) AS avg_speed
        FROM trips
        GROUP BY hour
        ORDER BY hour;
    """)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)


# Fetching sorted trips by duration using QuickSort
@api.route('/trips/sorted_by_duration')
def sorted_trips():
    cursor = connection.cursor()
    cursor.execute("SELECT trip_id, trip_duration, trip_distance_km, trip_speed_kmh FROM trips LIMIT 3")
    trips = cursor.fetchall()
    cursor.close()

    sorted_trips = quicksort_trips(trips)
    return jsonify(sorted_trips)

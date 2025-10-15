import MySQLdb
from MySQLdb.constants import CLIENT    # Enable LOCAL INFILE client flag


#  MySQL Login Details
user = "root"
password = "root"
database = "urban_mobility"

# Database connection
conn = MySQLdb.connect(
    host="127.0.0.1",
    user=user,
    passwd=password,
    port=3306,
    # Enable LOCAL INFILE on the client. Server must also allow it.
    client_flag=CLIENT.LOCAL_FILES,
    local_infile=1,
)

cursor = conn.cursor()

# Execute the schema SQL file to create the database and tables
with open('schema.sql', 'r') as f:
    schema_file = f.read()

# Split commands by ';' and execute each command
for command in schema_file.split(';'):
    if command.strip():  # Avoid executing empty commands
        cursor.execute(command)

# Try to enable local_infile for this session (may require server config)
try:
    cursor.execute("SET SESSION local_infile=1;")
except Exception:
    # If this fails it's likely the server has local_infile disabled in config.
    # Proceeding — the LOAD DATA LOCAL INFILE will still fail if server blocks it.
    pass

# Import CSV using LOAD DATA LOCAL INFILE directly into the MySQL table
csv_file = "cleaned_trips.csv"

load_csv_file = f"""
LOAD DATA LOCAL INFILE '{csv_file}'
INTO TABLE urban_mobility.trips
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
 pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude,
 store_and_fwd_flag, trip_duration, pickup_time, pickup_day_of_week, pickup_month, trip_distance_km, trip_speed_kmh, trip_distance_category);
"""

cursor.execute(load_csv_file)
cursor.close()
conn.commit()
conn.close()

print("Data imported successfully into the 'trips' table.")

from connection import connection # connect to MySQL database

# Check if connection was successful
if not connection:
    print("Connection to MySQL DB failed")
    exit(1)

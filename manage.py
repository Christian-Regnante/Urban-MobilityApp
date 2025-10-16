from connection import connection  # connect to MySQL database
import MySQLdb
from MySQLdb.constants import CLIENT    # Enable LOCAL INFILE client flag
import csv
import os
from datetime import datetime


#  MySQL Login Details
user = "root"
password = "Nopassword#.1"
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
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
 pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude,
 store_and_fwd_flag, trip_duration, pickup_time, pickup_day_of_week, pickup_month, trip_distance_km, trip_speed_kmh, trip_distance_category);
"""

try:
    # Try the fast server-side import first
    cursor.execute(load_csv_file)
    cursor.close()
    conn.commit()
    conn.close()
    print("Data imported successfully into the 'trips' table using LOAD DATA LOCAL INFILE.")
except MySQLdb.OperationalError as e:
    # Common case: server has local_infile disabled (error code 3948)
    err_msg = str(e)
    print(f"LOAD DATA LOCAL INFILE failed: {err_msg}")
    print("Falling back to Python-based CSV importer (slower but reliable).")

    # Re-open cursor in case it's closed or reuse existing connection
    try:
        cursor = conn.cursor()
    except Exception:
        conn = MySQLdb.connect(host="127.0.0.1", user=user,
                               passwd=password, port=3306, db=database)
        cursor = conn.cursor()

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    expected_cols = [
        'trip_id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime', 'passenger_count',
        'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
        'store_and_fwd_flag', 'trip_duration', 'pickup_time', 'pickup_day_of_week', 'pickup_month',
        'trip_distance_km', 'trip_speed_kmh', 'trip_distance_category'
    ]

    insert_sql = (
        "INSERT INTO urban_mobility.trips (" + ",".join(
            expected_cols) + ") VALUES (" + ",".join(["%s"] * len(expected_cols)) + ")"
    )

    batch_size = 1000
    rows_buffer = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        header_map = {name: idx for idx,
                      name in enumerate(header)} if header else {}
        # Support common header aliases from cleaned CSV
        if 'id' in header_map and 'trip_id' not in header_map:
            header_map['trip_id'] = header_map['id']
        # pickup_time may be absent in cleaned_trips.csv; ensure it is optional
        for i, row in enumerate(reader, start=1):
            # Build a mapped row in the expected DB column order using header names
            mapped_row = []
            # If pickup_time missing, we'll derive it from pickup_datetime
            for colname in expected_cols:
                if colname in header_map and header_map[colname] < len(row):
                    val = row[header_map[colname]]
                else:
                    val = None

                # Normalize empty strings to None so DB gets NULLs where appropriate
                if val == '':
                    val = None

                # Derive pickup_time from pickup_datetime if needed
                if colname == 'pickup_time' and (val is None or val == ''):
                    # attempt to extract time from pickup_datetime field
                    pd_idx = header_map.get('pickup_datetime')
                    if pd_idx is not None and pd_idx < len(row):
                        pd_val = row[pd_idx]
                        try:
                            dt = datetime.fromisoformat(pd_val)
                            val = dt.time().isoformat()
                        except Exception:
                            # try common datetime formats
                            try:
                                dt = datetime.strptime(
                                    pd_val, '%Y-%m-%d %H:%M:%S')
                                val = dt.time().isoformat()
                            except Exception:
                                val = None

                mapped_row.append(val)

            rows_buffer.append(tuple(mapped_row))

            if len(rows_buffer) >= batch_size:
                cursor.executemany(insert_sql, rows_buffer)
                conn.commit()
                print(f"Inserted {i} rows...")
                rows_buffer = []

    # Final batch
    if rows_buffer:
        cursor.executemany(insert_sql, rows_buffer)
        conn.commit()

    cursor.close()
    conn.close()
    print("Data imported successfully into the 'trips' table using Python fallback importer.")


# Check if connection was successful
if not connection:
    print("Connection to MySQL DB failed")
    exit(1)

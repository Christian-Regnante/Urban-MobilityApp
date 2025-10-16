# Urban-MobilityApp

A small Flask web application that connects to a MySQL database to store, query and serve urban mobility/trip data.

This repository includes utilities to clean a raw CSV of trips, create a database/schema, load cleaned data into MySQL, and run a Flask API that returns trip records and simple insights.

---

## Contents

- `app.py` - Flask application entrypoint
- `views.py` - Flask blueprints and API endpoints
- `connection.py` - MySQL connection helper (used by the app)
- `manage.py` - Creates schema and imports cleaned CSV into MySQL using `LOAD DATA LOCAL INFILE`
- `cleaning_train_data.py` - CSV cleaning pipeline that writes `cleaned_trips.csv`
- `algorithms.py` - Sorting helpers (quicksort/normalization)
- `requirements.txt` - Python dependencies
- `train.csv` / `train.zip` - (not included) raw dataset used by cleaning script
- `cleaned_trips.csv` - cleaned dataset produced by the cleaning script
- `templates/` and `static/` - simple UI (optional)

---

## Quickstart (Windows, PowerShell)

1. Clone the repository and open the folder:

   ```powershell
   git clone <repository-url>
   cd Urban-MobilityApp
   ```

2. Create and activate a virtual environment (Windows PowerShell):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Prepare the dataset:
   - Place `train.csv` (or `train.zip`) in the project root. The cleaning script will extract `train.csv` if `train.zip` is present.

   ```powershell
   python algorithms.py
   ```

   This produces `cleaned_trips.csv` which `manage.py` expects when importing into the database.

5. Configure your database connection:
   - Edit `connection.py` and `manage.py` to set your MySQL server credentials (host, user, password, port, database).
   - Make sure the target MySQL server is running and reachable from your machine.

6. Create schema and import cleaned data:
   - Note: `manage.py` uses `LOAD DATA LOCAL INFILE` to import CSV quickly. If your MySQL server has `local_infile` disabled, either enable it on the server or use a Python-based importer.

   ```powershell
   python manage.py
   ```

7. Run the Flask app (default port 3000):

   ```powershell
   python app.py
   ```

8. Visit the API endpoints
   - The app runs at `http://127.0.0.1:3000`
   - Base API root: `http://127.0.0.1:3000/api/`
   - Trips: `http://127.0.0.1:3000/api/trips`
   - Sorted by duration: `http://127.0.0.1:3000/api/trips/sorted_by_duration`
   - Average speed by hour: `http://127.0.0.1:3000/api/api/insights/average_speed`

---

## Database notes and troubleshooting

### LOAD DATA LOCAL INFILE fails with "Loading local data is disabled"

This repository's `manage.py` attempts to enable `local_infile` on the client and executes `LOAD DATA LOCAL INFILE`. Typical failure reasons and fixes:

- Server disabled `local_infile` in MySQL config (most common):
  - Edit `my.cnf` / `mysqld.cnf` or the server configuration and set:

    ```ini
    [mysqld]
    local_infile=1
    ```

  - Restart the MySQL server.

- Client needs the LOCAL flag enabled (the code sets client flags, but if importing fails you can use a Python loader as fallback):
  - Option 1 (server change) — prefer when you control the server.
  - Option 2 (Python fallback) — if you cannot change server settings, modify `manage.py` to import `cleaned_trips.csv` row-by-row using `csv` + parameterized INSERTs. This is slower but works when `LOAD DATA` is blocked.

### `MySQLdb` / `mysqlclient` and editor warnings

- If the code runs but your editor (Pylance/VSCode) shows `MySQLdb` unresolved, it's usually because the editor is not using the same virtual environment.
  - Select the interpreter in VSCode: `Ctrl+Shift+P` -> `Python: Select Interpreter` -> choose the project's venv.
  - Restart the language server or reload the window.
  - You can also create a small stub file under `typings/` to silence type-checking warnings.

---

## API reference

All responses are JSON.

- GET /api/trips
  - Returns a list of trip objects (by default the API uses `LIMIT 10000` in the code; you can change this in `views.py`).
  - Fields: `trip_id`, `vendor_id`, `pickup_datetime`, `dropoff_datetime`, `passenger_count`, `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, `dropoff_latitude`, `store_and_fwd_flag`, `trip_duration`, `pickup_time`, `pickup_day_of_week`, `pickup_month`, `trip_distance_km`, `trip_speed_kmh`, `trip_distance_category`.

- GET /api/trips/sorted_by_duration
  - Returns trips sorted ascending by `trip_duration`.
  - The endpoint uses the `algorithms.quicksort_trips` helper which normalizes DB rows and sorts by duration.

- GET /api/api/insights/average_speed
  - Returns average speed per pickup hour.

- GET /api/trips/filter?vendor_id=...&passenger_count=...&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  - Filtered results (the current implementation builds a parameterized query; review `views.py` for details and adjust LIMIT and protections as required).

---

## Developer notes

- `algorithms.py` contains a sorter that accepts both DB cursor rows (tuples) and dicts and returns a normalized list of dicts sorted by duration.
- It also runs `cleaning_train_data.py` which outputs `cleaned_trips.csv` used for fast import.
- `manage.py` will create schema from `schema.sql` — verify that `schema.sql` contains the expected CREATE statements and that it is not empty.

---

## Running tests / quick checks

- Quick import check (confirm `MySQLdb` is importable in your venv):

```powershell
& .\venv\Scripts\python.exe -c "import MySQLdb; print(MySQLdb.__file__)"
```

- Quick smoke test for the sorting helper:

```powershell
& .\venv\Scripts\python.exe -c "from algorithms import quicksort_trips; print(quicksort_trips([(1,10,1,1),(2,5,1,1)])))"
```

---

## Next improvements (suggested)

- Add a Python fallback CSV importer to `manage.py` for servers that disallow `LOAD DATA LOCAL INFILE`.
- Add unit tests for `algorithms.quicksort_trips` and the `views` endpoints.
- Add pagination and query parameters to `/api/trips` to make it more production-friendly.
- Add documentation of the DB schema (columns & types) in this README.

---

## Here are some result from `algorithms.py`
```bash
PS G:\ALU_classProjects\Urban-MobilityApp> & C:/Python313/python.exe g:/ALU_classProjects/Urban-MobilityApp/algorithms.py
train.zip was extracted successfully

Excluded 65 invalid records. Remaining: 1458579
✅ Cleaning complete. Saved as cleaned_trips.csv

✅ Sorting complete. Results saved as cleaned_trips.csv
          id  trip_duration  trip_distance_km  trip_speed_kmh
0  id2536510              1          0.008963       32.265740
1  id1520236              1          0.000643        2.313968
2  id0553321              1          0.133023      478.884427
3  id1491861              1          0.000424        1.527030
4  id0075470              1          0.000000        0.000000
```

---

** YOUTUBE VIDEO DEMO: **

[Urban Mobility App Demo](https://www.youtube.com/watch?v=3e5jv1n1HkY)

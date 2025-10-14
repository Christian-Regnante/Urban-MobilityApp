# Urban-MobilityApp

#### This repository contains a Flask web application that connects to a MySQL database to retrieve and display urban mobility data. The application provides an API endpoint to fetch trip data in JSON format.

## Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Urban-MobilityApp
   ```

2. After cloning first step, you have to create a virtual environment and activate it, for every application you run you need to have the venv activated:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. After creating the virtual environment, make sure to run this command to install the packages like modules used for this project(ex: Flask, MySQL connector, pandas, etc.), NOTE: Make sure you have activated the venv before running this command:
   ```bash
   pip install -r requirements.txt
   ```
**IMPORTANT**: 

- Make sure to download the train.csv file and place it in the same directory as `cleaning_train_data.py` file.

- Run the `cleaning_train_data.py` file to clean the CSV data and generate a new cleaned CSV file named `cleaned_trips_data.csv`:
   ```bash
   python cleaning_train_data.py
   ```

4. Set up the database connection:
   - Ensure you have MySQL workbench installed or any MySQL database server running.
   - Update the `connection.py` file with your MySQL database credentials.
   - And also update `manage.py` file connection details, between line 10-20 with your MySQL database credentials.

5. How to run the whole application:
    1. Run the `manage.py` file to create the database and table, and import the CSV data into the MySQL database:
       ```bash
       python manage.py
       ```
    2. Now you can run the actual Flask application after the above step is completed:
        - Navigate to `app.py` file then run the file or:
        ```bash
        python app.py
        ```
        - The port is set to `3000`
        - You can find the main routes in the `app.py` file, while the endpoint for fetching trip data is `/api/trips`, is in `views.py` file.

N.B: Make sure you are in the venv while running the above commands:
```bash
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Example you terminal should look like this:
```bash
(venv) PS G:\ALU_classProjects\Urban-MobilityApp> ...
```

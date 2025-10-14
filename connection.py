import MySQLdb
from MySQLdb import Error
# from MySQLdb.constants import CLIENT


# Connect to the MySQL server database
def connect_to_database():
    connection = None
    try:
        connection = MySQLdb.connect(
            host="127.0.0.1",
            user="root",
            port=3306,
            passwd="Nopassword#.1",
            db="urban_mobility",
            # # enable LOCAL INFILE on the client side; server must also allow it
            # client_flag=CLIENT.LOCAL_FILES,
            # local_infile=1,
        )
    except Error as e:
        print(f"An Error '{e}' occured while connecting to the database")

    return connection


connection = connect_to_database()

# if connection:
#     print("Connection to the database was successful")

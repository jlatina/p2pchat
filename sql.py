import mysql.connector

# Create a connection to the MySQL server
connection = mysql.connector.connect(host='localhost')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create a new database called "my_database"
database_name = 'client_database'
cursor.execute(f"CREATE DATABASE {database_name}")

# Close the cursor and connection to the server
cursor.close()
connection.close()

print(f"The {database_name} database was created successfully!")


"""
Database setup script for ALX_prodev with user_data table
"""

import mysql.connector
import csv
import uuid
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'ALX_prodev')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        print(f"Database {db_name} created/selected successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'ALX_prodev'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if connection.is_connected():
            print(f"Successfully connected to {os.getenv('DB_NAME', 'ALX_prodev')} database")
            return connection
    except Error as e:
        print(f"Error connecting to {os.getenv('DB_NAME', 'ALX_prodev')}: {e}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file):
    """Inserts data in the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Data already exists ({count} records). Skipping insertion.")
            cursor.close()
            return
        
        # Read CSV and insert data
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age) 
            VALUES (%s, %s, %s, %s)
            """
            
            for row in csv_reader:
                # Generate UUID if not provided
                user_id = str(uuid.uuid4())
                name = row.get('name', '')
                email = row.get('email', '')
                age = float(row.get('age', 0))
                
                cursor.execute(insert_query, (user_id, name, email, age))
            
            connection.commit()
            print(f"Successfully inserted {cursor.rowcount} records")
        
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")

# if __name__ == "__main__":
#     # Connect to MySQL server
#     connection = connect_db()
    
#     if connection:
#         # Create database ALX_prodev
#         create_database(connection)
        
#         # Connect to the ALX_prodev database
#         prodev_connection = connect_to_prodev()
        
#         if prodev_connection:
#             # Create user_data table
#             create_table(prodev_connection)
            
#             # Insert data from CSV file
#             csv_file_path = 'user_data.csv'
#             insert_data(prodev_connection, csv_file_path)
            
#             # Close the database connection
#             prodev_connection.close()
        
#         # Close the MySQL server connection
#         connection.close()
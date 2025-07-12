"""
Database setup script for ALX_prodev with users table using SQLite3
"""

import sqlite3
import csv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_db():
    """Connects to the SQLite database"""
    try:
        # Get database path from environment or use default
        db_path = os.getenv('DB_PATH', 'ALX_prodev.db')
        
        connection = sqlite3.connect(db_path)
        print(f"Successfully connected to SQLite database: {db_path}")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age REAL NOT NULL
        )
        """
        
        cursor.execute(create_table_query)
        
        # Create index for id (though it's already primary key)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_id ON users(id)")
        
        connection.commit()
        print("Table users created successfully")
        cursor.close()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file):
    """Inserts data in the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Data already exists ({count} records). Skipping insertion.")
            cursor.close()
            return
        
        # Read CSV and insert data
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            insert_query = """
            INSERT INTO users (name, email, age) 
            VALUES (?, ?, ?)
            """
            
            records_inserted = 0
            for row in csv_reader:
                # No need to generate id - SQLite will auto-increment
                name = row.get('name', '')
                email = row.get('email', '')
                age = float(row.get('age', 0))
                
                cursor.execute(insert_query, (name, email, age))
                records_inserted += 1
            
            connection.commit()
            print(f"Successfully inserted {records_inserted} records")
        
        cursor.close()
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
    except ValueError as e:
        print(f"Error converting data types: {e}")

def get_table_info(connection):
    """Displays information about the users table"""
    try:
        cursor = connection.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\nTable schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]}) - {'PRIMARY KEY' if column[5] else 'NOT NULL' if column[3] else 'NULLABLE'}")
        
        # Get record count
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\nTotal records: {count}")
        
        # Show first few records if any exist
        if count > 0:
            cursor.execute("SELECT * FROM users LIMIT 5")
            records = cursor.fetchall()
            print("\nFirst 5 records:")
            for record in records:
                print(f"  {record}")
        
        cursor.close()
    except sqlite3.Error as e:
        print(f"Error getting table info: {e}")

if __name__ == "__main__":
    # Connect to SQLite database
    connection = connect_db()
    
    if connection:
        # Create users table
        create_table(connection)
        
        # Insert data from CSV file
        csv_file_path = 'data/user_data.csv'
        insert_data(connection, csv_file_path)
        
        # Display table information
        get_table_info(connection)
        
        # Close the database connection
        connection.close()
        print("\nDatabase connection closed.")
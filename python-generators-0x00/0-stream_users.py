"""
Generator function that streams rows from the user_data table one by one
"""

import mysql.connector
from mysql.connector import Error
from db_config import db_config

def stream_users():
    """
    Generator function that yields user data one by one from the database
    
    Yields:
        dict: User data containing user_id, name, email, age
    """
    connection = None
    cursor = None
    
    try:
        # Connect to the database using config
        connection = db_config.connect()
        
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Execute query to fetch all users
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            # Yield one row at a time using the generator
            for row in cursor:
                yield {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'age': row['age']
                }
                
    except Error as e:
        print(f"Error reading data from MySQL: {e}")
    
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
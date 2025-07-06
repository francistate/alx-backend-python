#!/usr/bin/env python3
"""
Memory-efficient aggregation using generators to calculate average age
"""

import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def stream_user_ages():
    """
    Generator function that yields user ages one by one
    
    Yields:
        float: User age
    """
    connection = None
    cursor = None
    
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'ALX_prodev'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Execute query to fetch only ages (Loop 1: Database cursor iteration)
            cursor.execute("SELECT age FROM user_data")
            
            # Yield one age at a time
            for (age,) in cursor:
                yield float(age)
                
    except Error as e:
        print(f"Error reading data from MySQL: {e}")
        return
    
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def calculate_average_age():
    """
    Calculate the average age using the generator without loading
    the entire dataset into memory
    
    Returns:
        float: Average age of all users
    """
    total_age = 0
    count = 0
    
    # Loop 2: Use the generator to process ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0
    
    return total_age / count

# if __name__ == "__main__":
#     # Calculate and print the average age
#     average_age = calculate_average_age()
#     print(f"Average age of users: {average_age:.2f}")
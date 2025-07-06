"""
Batch processing with generators to fetch and process data in batches
"""

import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def stream_users_in_batches(batch_size):
    """
    Generator function that fetches users in batches
    
    Args:
        batch_size (int): Number of users to fetch in each batch
        
    Yields:
        list: Batch of user dictionaries
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
            cursor = connection.cursor(dictionary=True)
            
            offset = 0
            
            # Loop 1: Main batch fetching loop
            while True:
                # Fetch batch of users with LIMIT and OFFSET
                query = f"SELECT user_id, name, email, age FROM user_data LIMIT {batch_size} OFFSET {offset}"
                cursor.execute(query)
                
                batch = cursor.fetchall()
                
                # If no more data, break the loop
                if not batch:
                    break
                
                # Yield the batch
                yield batch
                
                # Increment offset for next batch
                offset += batch_size
                
    except Error as e:
        print(f"Error reading data from MySQL: {e}")
        return
    
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_processing(batch_size):
    """
    Generator function that processes each batch to filter users over the age of 25
    
    Args:
        batch_size (int): Size of each batch to process
        
    Yields:
        dict: User data for users over age 25
    """
    # Loop 2: Process each batch from the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Filter users over age 25 in current batch
        for user in batch:
            if user['age'] > 25:
                yield user
                # print(f"User ID: {user['user_id']}, Name: {user['name']}, Email: {user['email']}, Age: {user['age']}")

# # # Example usage
# if __name__ == "__main__":
#     batch_size = 10  # Define the batch size
#     batch_processing(batch_size)
    
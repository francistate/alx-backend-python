#!/usr/bin/env python3
"""
Lazy loading paginated data using generators
"""

import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def paginate_users(page_size, offset):
    """
    Fetch a specific page of users from the database
    
    Args:
        page_size (int): Number of users per page
        offset (int): Number of records to skip
        
    Returns:
        list: List of user dictionaries for the requested page
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
            
            # Execute query with LIMIT and OFFSET
            query = f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}"
            cursor.execute(query)
            
            rows = cursor.fetchall()
            return rows
            
    except Error as e:
        print(f"Error reading data from MySQL: {e}")
        return []
    
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def lazy_paginate(pagesize):
    """
    Generator function that lazily loads pages of users
    
    Args:
        pagesize (int): Number of users per page
        
    Yields:
        list: Page of user data (list of dictionaries)
    """
    offset = 0
    
    # Single loop: Continue until no more data
    while True:
        # Get the next page using paginate_users function
        page = paginate_users(pagesize, offset)
        
        # If no data returned, we've reached the end
        if not page:
            break
            
        # Yield the current page (lazy loading - only when requested)
        yield page
        
        # Move to next page
        offset += pagesize

# Alternative name for the function (matching the import in main file)
lazy_pagination = lazy_paginate

# # Example usage
if __name__ == "__main__":
    page_size = 10  # Define the page size
    for i, page in enumerate(lazy_paginate(page_size)):
        print(f"Page {i + 1}:")
        for user in page:
            print(user)
        print()
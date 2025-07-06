"""
Database configuration module
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME', 'ALX_prodev')
        self.port = int(os.getenv('DB_PORT', 3306))
        
        # Validate required environment variables
        if not self.password:
            raise ValueError("DB_PASSWORD environment variable is required")
    
    def get_connection_params(self, include_db=True):
        """Get connection parameters as a dictionary"""
        params = {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'port': self.port
        }
        
        if include_db:
            params['database'] = self.database
            
        return params
    
    def connect(self, include_db=True):
        """Create a database connection"""
        try:
            params = self.get_connection_params(include_db)
            connection = mysql.connector.connect(**params)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"Successfully connected to MySQL Server version {db_info}")
                return connection
                
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def test_connection(self):
        """Test database connection"""
        connection = self.connect(include_db=False)
        if connection:
            connection.close()
            return True
        return False

# Create a global instance
db_config = DatabaseConfig()
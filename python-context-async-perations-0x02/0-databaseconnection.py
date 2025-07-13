"""
Custom class-based context manager for database connections
"""

import sqlite3


class DatabaseConnection:
    """
    A custom context manager class to handle database connections
    automatiaclly opens and closes database connections
    """
    
    def __init__(self, db_path):
        """
        Initialize the DatabaseConnection with database path
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context manager - establish database connection
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
            return self
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - close database connection
        
        Args:
            exc_type: Exception type (if any)
            exc_value: Exception value (if any)
            traceback: Exception traceback (if any)
        """
        if self.connection:
            if exc_type is None:
                # no exception occurred, commit any pending transaction
                self.connection.commit()
                print("Transaction committed successfully")
            else:
                # an exception occurred, rollback any pending transaction
                self.connection.rollback()
                print(f"Transaction rolled back due to error: {exc_value}")
            
            # close the connection
            self.connection.close()
            print("Database connection closed")
        
        # return False to propagate any exception that occurred
        return False
    

    def execute_query(self, query):
        """
        Execute a query and return results as a generator
        
        Args:
            query (str): SQL query to execute
            
        Yields:
            tuple: Each row from the query result
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                yield row
        finally:
            cursor.close()

# # Example usage of the DatabaseConnection context manager
# def main():
#     db_path = 'users.db'
    
#     # using the DatabaseConnection context manager
#     with DatabaseConnection(db_path) as db_conn:
#         # example query to fetch all users
#         query = "SELECT * FROM users"
        
#         # Using the generator to fetch results
#         for row in db_conn.execute_query(query):
#             print(row)

# if __name__ == "__main__":
#     main()
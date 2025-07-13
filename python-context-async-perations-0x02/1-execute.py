"""
Query Context Manager
"""

import sqlite3


class ExecuteQuery:
    """
    A reusable context manager class that executes SQL queries
    Manages both database connection and query execution
    """
    
    def __init__(self, db_path, query, params=None):
        """
        Initialize the ExecuteQuery context manager
        
        Args:
            db_path (str): Path to the SQLite database file
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
        """
        self.db_path = db_path
        self.query = query
        self.params = params or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - establish connection and execute query    
        Returns:
            list: Results of the executed query
        """
        try:
            # establish database connection
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
            
            # create cursor and execute qeury
            self.cursor = self.connection.cursor()
            self.cursor.execute(self.query, self.params)
            
            # fetch all results
            self.results = self.cursor.fetchall()
            print(f"Query executed successfully. Retrieved {len(self.results)} rows.")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - clean up resources
        
        Args:
            exc_type: Exception type (if any)
            exc_value: Exception value (if any)
            traceback: Exception traceback (if any)
        """
        # close cursor if it exists
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        
        # handle connection cleanup
        if self.connection:
            if exc_type is None:
                # if no exception occurred, commit any pending transaction
                self.connection.commit()
                print("Transaction committed successfully")
            else:
                # if an exception occurred, rollback any pending transaction
                self.connection.rollback()
                print(f"Transaction rolled back due to error: {exc_value}")
            
            # close the connection
            self.connection.close()
            print("Database connection closed")
        
        # return false to propagate any exception that occurred
        return False


def main():
    """
    Main function to demonstrate the ExecuteQuery context manager
    """
    db_path = 'users.db'
    query = "SELECT * FROM users WHERE age > ?"
    age_param = 25
    
    # using the ExecuteQuery context manager
    with ExecuteQuery(db_path, query, (age_param,)) as results:
        print(f"Users with age > {age_param}:")
        print("-" * 65)
        
        if results:
            for row in results:
                print(row)
        else:
            print("No users found matching the criteria.")


if __name__ == "__main__":
    main()
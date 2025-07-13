import time
import sqlite3 
import functools


query_cache = {}

def with_db_connection(func):
    """ your code goes here""" 
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connection = sqlite3.connect('users.db')
        try:
            result = func(connection, *args, **kwargs)
            return result
        finally:
            connection.close()
    return wrapper



def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] is connection, args[1] is query
        # or query might be in kwargs
        query = args[1] if len(args) > 1 else kwargs.get('query', '')
        
        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
        
        print(f"Executing SQL Query: {query}")
        result = func(*args, **kwargs)
        query_cache[query] = result  # cache the result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
import sqlite3 
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connection = sqlite3.connect('users.db')
        try:
            result = func(connection, *args, **kwargs)
            return result
        finally:
            connection.close()
    return wrapper


#  decorator to handle database transactions
def transactional(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connection = args[0]  # ssuming the first argument is the database connection
        try:
            result = func(*args, **kwargs)
            connection.commit()  # commit if no exception occurs
            return result
        except Exception as e:
            connection.rollback()  # rollback on error
            print(f"Transaction failed: {e}")
            raise  # raise the exception again for further handling if needed
    return wrapper


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
    #### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
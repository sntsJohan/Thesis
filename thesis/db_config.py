import pyodbc
import traceback

def get_db_connection():
    """
    Get a connection to the SQL Server database
    
    Returns:
        Connection object or raises an exception
    """
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=cbdstipqc.database.windows.net;'  # From Azure
            'DATABASE=Thesis_db;'                     # Your DB name
            'UID=;'                          # Your admin username
            'PWD=;'                  # Your password
            'Connection Timeout=30;'                  # Add timeout
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        print(traceback.format_exc())
        raise  # Re-raise to allow caller to handle it

def test_connection():
    """
    Test if the database connection is working
    
    Returns:
        tuple: (bool, str) - (success, error_message)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@version")
        version = cursor.fetchone()[0]
        conn.close()
        return True, f"Connection successful: {version.split()[0]}"
    except Exception as e:
        error_msg = f"Database connection failed: {str(e)}"
        return False, error_msg

def log_user_action(username, action):
    """
    Log user actions to the database
    
    Args:
        username (str): Username of the user
        action (str): Description of the action
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_logs (username, action, timestamp)
            VALUES (?, ?, GETDATE())
        ''', (username, action))
        conn.commit()
    except Exception as e:
        print(f"Logging error: {str(e)}")
        print(traceback.format_exc())
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

import pyodbc

def get_db_connection():
       conn = pyodbc.connect(
           'DRIVER={ODBC Driver 17 for SQL Server};'
           'SERVER=cbdstipqc.database.windows.net;'  # From Azure
           'DATABASE=Thesis_db;'                         # Your DB name
           'UID=sntsyohan;'                           # Your admin username
           'PWD=09499894635Johan!;'                        # Your password
       )
       return conn

def log_user_action(username, action):
    """Log user actions to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_logs (username, action, timestamp)
            VALUES (?, ?, GETDATE())
        ''', (username, action))
        conn.commit()
    except Exception as e:
        print(f"Logging error: {str(e)}")
    finally:
        conn.close()

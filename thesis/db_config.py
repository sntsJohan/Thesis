import pyodbc

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=YOHAN\SQLEXPRESS;'
        'DATABASE=Thesis;'
        'Trusted_Connection=yes;'
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

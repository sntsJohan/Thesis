import pyodbc

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=YOHAN\SQLEXPRESS;'
        'DATABASE=Thesis;'
        'Trusted_Connection=yes;'
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL
        )
    ''')
    
    # Insert default admin and user if they don't exist
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM users WHERE username='admin')
        INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')
    ''')
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM users WHERE username='user')
        INSERT INTO users (username, password, role) VALUES ('user', 'user123', 'user')
    ''')
    
    conn.commit()
    conn.close()

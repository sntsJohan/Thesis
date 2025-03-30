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
    
    # Create tabs table
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabs' AND xtype='U')
        CREATE TABLE tabs (
            tab_id INT IDENTITY(1,1) PRIMARY KEY,
            tab_name VARCHAR(100) NOT NULL,
            tab_type VARCHAR(50) NOT NULL,
            creation_date DATETIME DEFAULT GETDATE(),
            username VARCHAR(50) NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Create comments table
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
        CREATE TABLE comments (
            comment_id INT IDENTITY(1,1) PRIMARY KEY,
            comment_text NVARCHAR(MAX) NOT NULL,
            prediction VARCHAR(50) NOT NULL,
            confidence FLOAT NOT NULL,
            analysis_date DATETIME DEFAULT GETDATE()
        )
    ''')
    
    # Create comment metadata table
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comment_metadata' AND xtype='U')
        CREATE TABLE comment_metadata (
            comment_id INT PRIMARY KEY,
            profile_name NVARCHAR(100),
            profile_picture NVARCHAR(MAX),
            post_date DATETIME,
            likes_count INT,
            profile_id VARCHAR(100),
            is_reply BIT DEFAULT 0,
            reply_to_comment_id INT,
            FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
            FOREIGN KEY (reply_to_comment_id) REFERENCES comments(comment_id)
        )
    ''')
    
    # Create tab_comments junction table
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tab_comments' AND xtype='U')
        CREATE TABLE tab_comments (
            tab_id INT,
            comment_id INT,
            display_order INT NOT NULL,
            PRIMARY KEY (tab_id, comment_id),
            FOREIGN KEY (tab_id) REFERENCES tabs(tab_id),
            FOREIGN KEY (comment_id) REFERENCES comments(comment_id)
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

def save_tab(username, tab_name, tab_type, comments_data):
    """Save a tab and its comments to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create new tab
        cursor.execute('''
            INSERT INTO tabs (tab_name, tab_type, username)
            VALUES (?, ?, ?)
        ''', (tab_name, tab_type, username))
        
        # Get the tab_id
        cursor.execute("SELECT SCOPE_IDENTITY()")
        tab_id = cursor.fetchone()[0]
        
        # Insert comments and their metadata
        for i, data in enumerate(comments_data):
            # Insert comment
            cursor.execute('''
                INSERT INTO comments (comment_text, prediction, confidence)
                VALUES (?, ?, ?)
            ''', (data['text'], data['prediction'], data['confidence']))
            
            # Get comment_id
            cursor.execute("SELECT SCOPE_IDENTITY()")
            comment_id = cursor.fetchone()[0]
            
            # Insert metadata
            cursor.execute('''
                INSERT INTO comment_metadata 
                (comment_id, profile_name, profile_picture, post_date, 
                likes_count, profile_id, is_reply, reply_to_comment_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (comment_id, data['metadata']['profile_name'],
                 data['metadata']['profile_picture'],
                 data['metadata']['date'],
                 data['metadata']['likes_count'],
                 data['metadata']['profile_id'],
                 data['metadata'].get('is_reply', False),
                 data['metadata'].get('reply_to', None)))
            
            # Link comment to tab with display order
            cursor.execute('''
                INSERT INTO tab_comments (tab_id, comment_id, display_order)
                VALUES (?, ?, ?)
            ''', (tab_id, comment_id, i))
        
        # Commit transaction
        conn.commit()
        return tab_id
        
    except Exception as e:
        cursor.execute("ROLLBACK TRANSACTION")
        raise e
    finally:
        conn.close()

def get_user_tabs(username):
    """Get all tabs for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tab_id, tab_name, tab_type, creation_date
        FROM tabs
        WHERE username = ?
        ORDER BY creation_date DESC
    ''', username)
    
    return cursor.fetchall()

def get_tab_comments(tab_id):
    """Get all comments and their metadata for a tab"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.comment_text, c.prediction, c.confidence,
            m.profile_name, m.profile_picture, m.post_date,
            m.likes_count, m.profile_id, m.is_reply, m.reply_to_comment_id
        FROM tab_comments tc
        JOIN comments c ON tc.comment_id = c.comment_id
        JOIN comment_metadata m ON c.comment_id = m.comment_id
        WHERE tc.tab_id = ?
        ORDER BY tc.display_order
    ''', tab_id)
    
    return cursor.fetchall()

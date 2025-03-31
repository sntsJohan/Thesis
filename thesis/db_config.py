import pyodbc

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=YOHAN\SQLEXPRESS;'
        'DATABASE=Thesis;'
        'Trusted_Connection=yes;'
    )
    return conn

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

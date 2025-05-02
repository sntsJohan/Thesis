from db_config import get_db_connection
import traceback

def test_api_table_connection():
    """
    Test the connection to the database and check if the api_keys table exists
    
    Returns:
        tuple: (bool, str) - (success, error_message)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the api_keys table exists
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'api_keys'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            return False, "The api_keys table doesn't exist in the database"
        
        # Test if we can query the table
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        count = cursor.fetchone()[0]
        
        return True, f"Connection successful. Found {count} API keys."
    except Exception as e:
        error_msg = f"Database connection error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return False, error_msg
    finally:
        if conn:
            conn.close()

def get_api_key(key_name='apify'):
    """
    Get an API key from the database
    
    Args:
        key_name (str): The name of the API key to retrieve
        
    Returns:
        str: The API key if found, or None if not found
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT api_key FROM api_keys 
            WHERE key_name = ? AND is_active = 1
        ''', (key_name,))
        
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error retrieving API key: {str(e)}")
        print(traceback.format_exc())
        return None
    finally:
        if conn:
            conn.close()

def set_api_key(key_name, api_key):
    """
    Update or insert an API key in the database
    
    Args:
        key_name (str): The name of the API key
        api_key (str): The API key value
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if the table exists
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'api_keys'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            # Create the table if it doesn't exist
            cursor.execute('''
                CREATE TABLE api_keys (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    key_name NVARCHAR(50) NOT NULL,
                    api_key NVARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE(),
                    is_active BIT DEFAULT 1
                )
            ''')
            conn.commit()
            print("Created api_keys table")
        
        # Check if key exists
        cursor.execute('''
            SELECT COUNT(*) FROM api_keys 
            WHERE key_name = ?
        ''', (key_name,))
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            # Update existing key
            cursor.execute('''
                UPDATE api_keys
                SET api_key = ?, updated_at = GETDATE()
                WHERE key_name = ?
            ''', (api_key, key_name))
        else:
            # Insert new key
            cursor.execute('''
                INSERT INTO api_keys (key_name, api_key)
                VALUES (?, ?)
            ''', (key_name, api_key))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error setting API key: {str(e)}")
        print(traceback.format_exc())
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_all_api_keys():
    """
    Get all API keys from the database
    
    Returns:
        list: List of dictionaries containing key_name and api_key
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if the table exists
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'api_keys'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("api_keys table doesn't exist")
            return []
            
        cursor.execute('''
            SELECT key_name, api_key, is_active 
            FROM api_keys
            ORDER BY key_name
        ''')
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error retrieving API keys: {str(e)}")
        print(traceback.format_exc())
        return []
    finally:
        if conn:
            conn.close()

def delete_api_key(key_name):
    """
    Delete an API key from the database
    
    Args:
        key_name (str): The name of the API key to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM api_keys
            WHERE key_name = ?
        ''', (key_name,))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting API key: {str(e)}")
        print(traceback.format_exc())
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close() 
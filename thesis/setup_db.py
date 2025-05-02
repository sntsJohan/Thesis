from db_config import get_db_connection, test_connection
import os
import traceback

def setup_database():
    """
    Verify and set up the database tables if needed
    """
    # First test basic connectivity
    connected, error_message = test_connection()
    if not connected:
        print(f"ERROR: Database connection failed: {error_message}")
        return False
        
    print("Database connection successful")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if API keys table exists
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'api_keys'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            # Create the table if it doesn't exist
            print("API keys table does not exist, creating it now...")
            cursor.execute('''
                CREATE TABLE api_keys (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    key_name NVARCHAR(50) NOT NULL UNIQUE,
                    api_key NVARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE(),
                    is_active BIT DEFAULT 1
                )
            ''')
            conn.commit()
            print("Created api_keys table")
        else:
            print("API keys table exists")
            
        # Check if we need to migrate the API key from the hardcoded source
        cursor.execute("SELECT COUNT(*) FROM api_keys WHERE key_name = 'apify'")
        if cursor.fetchone()[0] == 0:
            try:
                # Try to read the API key from scraper.py
                import re
                scraper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper.py')
                
                if os.path.exists(scraper_path):
                    with open(scraper_path, 'r') as file:
                        content = file.read()
                        api_match = re.search(r'api = ["\'](.+?)["\']', content)
                        
                        if api_match:
                            api_key = api_match.group(1)
                            cursor.execute('''
                                INSERT INTO api_keys (key_name, api_key)
                                VALUES (?, ?)
                            ''', ('apify', api_key))
                            
                            print("Migrated API key from scraper.py to database")
            except Exception as e:
                print(f"Error migrating API key: {str(e)}")
                print(traceback.format_exc())
                
                # Add default key if migration failed and no key exists
                cursor.execute('''
                    INSERT INTO api_keys (key_name, api_key)
                    VALUES (?, ?)
                ''', ('apify', 'apify_api_BWinyy1TCK8cFaOvdeCUQqAtBjJSvY2XdHMo'))
        
        conn.commit()
        print("Database verification completed successfully.")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database setup error: {str(e)}")
        print(traceback.format_exc())
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("Database setup completed successfully")
    else:
        print("Database setup failed, please check the errors") 
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lirui4689321',
    'database': 'ai_code_review',
    'charset': 'utf8mb4'
}

def update_table_timestamps():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to MySQL successfully!")
        
        cursor.execute("ALTER TABLE code_files MODIFY created_at DATETIME DEFAULT (NOW())")
        cursor.execute("ALTER TABLE code_files MODIFY updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW()")
        
        cursor.execute("ALTER TABLE analysis_results MODIFY created_at DATETIME DEFAULT (NOW())")
        
        cursor.execute("ALTER TABLE review_sessions MODIFY created_at DATETIME DEFAULT (NOW())")
        cursor.execute("ALTER TABLE review_sessions MODIFY updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW()")
        
        cursor.execute("ALTER TABLE review_comments MODIFY created_at DATETIME DEFAULT (NOW())")
        
        cursor.execute("ALTER TABLE users MODIFY created_at DATETIME DEFAULT (NOW())")
        cursor.execute("ALTER TABLE users MODIFY updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW()")
        
        cursor.execute("ALTER TABLE projects MODIFY created_at DATETIME DEFAULT (NOW())")
        cursor.execute("ALTER TABLE projects MODIFY updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW()")
        
        conn.commit()
        
        print("All tables updated successfully!")
        
        cursor.execute("SELECT NOW()")
        current_time = cursor.fetchone()[0]
        print(f"Current database time: {current_time}")
        
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_table_timestamps()

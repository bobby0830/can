import sqlite3
import os

DATABASE = os.getenv('DATABASE', 'calendar_app.db')

def init_db():
    # 確保資料庫資料夾存在
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        interests TEXT
    )
    ''')
    
    # Create events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        title TEXT,
        description TEXT,
        reason TEXT,
        link TEXT,
        category TEXT,
        embedding BLOB
    )
    ''')

    # 檢查並新增缺失的欄位 (簡單遷移)
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN verified INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE events ADD COLUMN updated_at TEXT")
    except sqlite3.OperationalError:
        # 欄位已存在
        pass
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")











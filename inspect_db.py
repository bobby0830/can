import sqlite3
import numpy as np
import os

DATABASE = 'backend/calendar_app.db' # Try both possible paths

def check_db(db_path):
    if not os.path.exists(db_path):
        print(f"File {db_path} not found.")
        return
    
    print(f"--- Checking database: {db_path} ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, title, date, description FROM events LIMIT 20")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]} | Date: {row[2]} | Title: {row[1]}")
            print(f"Desc: {row[3][:100]}...")
            print("-" * 30)
            
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"Total events in DB: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Check common locations
    check_db('calendar_app.db')
    check_db('backend/calendar_app.db')
    # Since it's in docker, it might be in the root or backend folder depending on where I'm running from

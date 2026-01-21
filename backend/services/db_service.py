import sqlite3
import json
import numpy as np
import os

DATABASE = os.getenv('DATABASE', 'calendar_app.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def save_events_to_db(events_with_embeddings):
    """
    將提取的事件及其向量存入資料庫。
    使用向量相似度來辨識並合併語義相同的活動。
    """
    from services.recommender import util
    import torch
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 獲取資料庫現有的所有事件及其向量以便比對
    existing_events = get_all_events_from_db()
    
    saved_count = 0
    updated_count = 0
    
    for new_event in events_with_embeddings:
        new_emb = torch.from_numpy(new_event['embedding'])
        is_duplicate = False
        duplicate_id = None
        
        # 1. 優先精確標題比對
        for ex in existing_events:
            if ex['title'].lower() == new_event['title'].lower():
                is_duplicate = True
                duplicate_id = ex.get('id')
                break
        
        # 2. 如果標題沒對上，進行向量相似度比對
        if not is_duplicate and existing_events:
            for ex in existing_events:
                if ex['embedding'] is not None:
                    ex_emb = torch.from_numpy(ex['embedding'])
                    similarity = util.cos_sim(new_emb, ex_emb).item()
                    
                    if similarity > 0.88: # 高靈敏度去重
                        is_duplicate = True
                        duplicate_id = ex.get('id')
                        break
        
        embedding_blob = np.array(new_event['embedding'], dtype=np.float32).tobytes()
        verified = 1 if new_event.get('verified') else 0
        updated_at = new_event.get('updated', '')
        
        if is_duplicate and duplicate_id:
            # 智慧合併：如果新抓到的日期更準確 (非 2026-01-00)，則更新
            cursor.execute("SELECT date, description, verified FROM events WHERE id = ?", (duplicate_id,))
            current = cursor.fetchone()
            
            needs_update = False
            # 如果舊日期是預設值且新日期不是
            if (current[0] in ['2026-01-00', '2026-01-01', 'TBD']) and (new_event['date'] not in ['2026-01-00', 'TBD']):
                needs_update = True
            # 如果新描述更詳細
            if len(new_event.get('description', '')) > len(current[1]) + 20:
                needs_update = True
            # 如果新資料已驗證而舊資料未驗證
            if verified > current[2]:
                needs_update = True
                
            if needs_update:
                cursor.execute('''
                UPDATE events 
                SET date = ?, description = ?, embedding = ?, link = ?, category = ?, verified = ?, updated_at = ?
                WHERE id = ?
                ''', (new_event['date'], new_event['description'], embedding_blob, 
                      new_event['link'], new_event.get('category', 'other'), 
                      verified, updated_at, duplicate_id))
                updated_count += 1
            continue
            
        # 3. 插入全新事件
        cursor.execute('''
        INSERT INTO events (date, title, description, link, category, verified, updated_at, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (new_event.get('date', '2026-01-00'), new_event['title'], new_event.get('description', ''), 
              new_event.get('link', ''), new_event.get('category', 'other'), 
              verified, updated_at, embedding_blob))
        saved_count += 1
        
    conn.commit()
    conn.close()
    print(f"  [DB] Smart Save: {saved_count} new, {updated_count} merged/updated.")

def clear_all_events():
    """
    清空資料庫中的所有事件。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")
    conn.commit()
    conn.close()
    print("  [DB] All events cleared.")

def get_all_events_from_db():
    """
    從資料庫取出所有事件及其向量。包含 ID 以便更新。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, date, description, link, category, verified, updated_at, embedding FROM events")
    rows = cursor.fetchall()
    
    events = []
    for row in rows:
        events.append({
            'id': row['id'],
            'title': row['title'],
            'date': row['date'],
            'description': row['description'],
            'link': row['link'],
            'category': row['category'],
            'verified': row['verified'],
            'updated_at': row['updated_at'],
            'embedding': np.frombuffer(row['embedding'], dtype=np.float32) if row['embedding'] else None
        })
    
    conn.close()
    return events

def count_events_in_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def export_events_to_csv(output_path):
    """
    將資料庫中的所有事件導出為 CSV 文件。
    """
    import csv
    events = get_all_events_from_db()
    if not events:
        return False
        
    keys = ['title', 'date', 'description', 'link', 'verified']
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            for e in events:
                row = {k: v for k, v in e.items() if k in keys}
                dict_writer.writerow(row)
        return True
    except Exception as e:
        print(f"  [DB] Export failed: {e}")
        return False

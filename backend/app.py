from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
from services.search_service import search_events
from services.recommender import get_recommendations, get_recommendations_from_list
from services.db_service import get_all_events_from_db, count_events_in_db, export_events_to_csv, clear_all_events
from database import init_db

app = Flask(__name__)
CORS(app)

DATABASE = os.getenv('DATABASE', 'calendar_app.db')

# 確保資料庫已初始化
init_db()

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        clear_all_events()
        return jsonify({"status": "success", "message": "Cache cleared."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/export', methods=['GET'])
def export_data():
    try:
        export_path = '/app/data/events_export.csv'
        success = export_events_to_csv(export_path)
        if success:
            from flask import send_file
            return send_file(export_path, as_attachment=True)
        else:
            return jsonify({"error": "No data to export"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Calendar Suggestion API is running."

@app.route('/user/profile', methods=['POST'])
def save_profile():
    data = request.json
    username = data.get('username', 'default_user')
    interests = data.get('interests', [])
    
    interests_str = ", ".join(interests)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO users (username, interests) VALUES (?, ?)
    ''', (username, interests_str))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Profile saved."})

import traceback

@app.route('/recommendations', methods=['GET'])
def fetch_recommendations():
    try:
        username = request.args.get('username', 'default_user')
        
        # 獲取用戶興趣
        conn = get_db()
        user = conn.execute('SELECT interests FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({"events": []})
        
        interests = user['interests']
        print(f"Fetching recommendations for interests: {interests}")
        
        # 為了提升語義匹配準確率，準備一個英文版的興趣詞供推薦模型使用
        interests_en = interests.replace("機器學習", "Machine Learning")\
                                .replace("人工智慧", "AI")\
                                .replace("機器人", "Robotics")\
                                .replace("大數據", "Big Data")\
                                .replace("美國金融", "US Finance")\
                                .replace("美國政治", "US Politics")
        
        # 1. 優先從資料庫獲取所有已存事件
        db_events = get_all_events_from_db()
        print(f"  [Flow] Found {len(db_events)} events in local database.")
        
        # 2. 智慧觸發搜尋：判斷現有資料是否與當前興趣相關
        is_fresh_search_needed = True
        if db_events:
            # 先試著從現有資料庫做一次初步篩選
            temp_recommendations = get_recommendations_from_list(interests_en, db_events)
            high_score_count = len([e for e in temp_recommendations if e['score'] >= 0.35])
            
            print(f"  [Flow] Local highly relevant events count: {high_score_count}")
            # 如果資料庫裡已經有足夠多(例如 4 個以上)高度相關的事件，就不需要即時搜尋
            if high_score_count >= 4:
                is_fresh_search_needed = False
                print(f"  [Flow] Sufficient local cache found. Skipping live search.")

        if is_fresh_search_needed:
            print(f"  [Flow] Not enough relevant data, triggering live search for: {interests}")
            search_events(interests) 
            db_events = get_all_events_from_db() # 重新獲取入庫後的資料
            
        # 3. 執行最終向量推薦
        recommended_events = get_recommendations_from_list(interests_en, db_events)
        
        # 4. 過濾分數門檻：提升到 0.25，確保只有真正相關的才會顯示
        # 移除之前的「強制回傳前 3 個」邏輯，避免顯示不相關的舊快取
        filtered_events = [e for e in recommended_events if e['score'] >= 0.25]
            
        print(f"Returning {len(filtered_events)} filtered events.")
        if filtered_events:
            print(f"DEBUG: First event content: {json.dumps(filtered_events[0], ensure_ascii=False)}")
        return jsonify({"events": filtered_events})
        
    except Exception as e:
        print("!!! ERROR IN RECOMMENDATIONS !!!")
        traceback.print_exc()
        return jsonify({"error": str(e), "events": []}), 500

if __name__ == '__main__':
    # 啟用 debug 模式以在 Docker 日誌中看到詳細錯誤
    app.run(debug=True, host='0.0.0.0', port=5000)

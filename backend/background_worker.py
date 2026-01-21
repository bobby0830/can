import time
import json
import os
import logging
import requests
import asyncio
from datetime import datetime
from services.search_service import duckduckgo_html_search
from services.mcp_wrapper import call_mcp_search
from services.crawler_utils import crawl_and_extract
from services.db_service import save_events_to_db, count_events_in_db
from services.recommender import compute_embedding
from services.llm_service import DEEPSEEK_API_KEY, DEEPSEEK_URL, MODEL_NAME

# --- 設定區 ---
OLLAMA_URL = "http://host.docker.internal:11434/api/generate" # 如果在 Docker 外執行請改為 localhost
OLLAMA_MODEL = "llama3"
KEYWORDS_FILE = "searched_keywords.json"
LOG_FILE = "worker.log"

# 設定 Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)

def call_ollama(prompt):
    """呼叫本地 Ollama 模型"""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=120)
        return json.loads(response.json()['response'])
    except Exception as e:
        logging.error(f"Ollama 呼叫失敗: {e}")
        return None

def generate_new_keywords(history):
    """步驟 2: 使用本地模型生成新關鍵字"""
    prompt = f"""
    You are an expert event researcher. Based on the following list of already searched keywords, 
    generate 10 NEW and specific search keywords for technology, AI, finance, or global events happening in 2026.
    Focus on niche conferences, product releases, or earnings.
    History: {history[-20:]}
    Output ONLY a JSON list of strings: ["kw1", "kw2", ...]
    """
    logging.info("正在使用 Ollama 生成新關鍵字...")
    res = call_ollama(prompt)
    return res if isinstance(res, list) else []

def local_extract_events(markdown):
    """步驟 3: 使用本地模型初步歸納資訊"""
    prompt = f"""
    Extract all 2026 events from the following text. 
    Output a JSON list of objects: {{"title": "...", "date": "YYYY-MM-DD or 2026-01-00", "description": "..."}}
    Text: {markdown[:5000]}
    """
    res = call_ollama(prompt)
    return res if isinstance(res, list) else []

def verify_with_deepseek(events_batch):
    """步驟 4: 使用 DeepSeek API 批量檢查"""
    if not events_batch: return []
    
    prompt = f"""
    你是一個專業的資料審核員。請檢查以下事件列表是否符合：
    1. 確實是 2026 年的活動。
    2. 活動名稱與日期是否真實存在（拒絕幻覺）。
    3. 日期格式是否正確 (YYYY-MM-DD)。
    
    待檢查列表：{json.dumps(events_batch)}
    
    請修正錯誤，過濾掉虛假或非 2026 的活動，僅返回驗證過的 JSON 列表。
    """
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        logging.info(f"正在透過 DeepSeek 驗證 {len(events_batch)} 個事件...")
        res = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        data = json.loads(content)
        # 處理可能的 JSON 嵌套
        for k in data:
            if isinstance(data[k], list): return data[k]
        return []
    except Exception as e:
        logging.error(f"DeepSeek 驗證失敗: {e}")
        return []

async def run_cycle():
    """單次自動化循環"""
    # 1. 讀取歷史
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = ["AI conferences 2026", "NVIDIA earnings 2026", "CES 2026"]

    # 2. 生成關鍵字
    new_kws = generate_new_keywords(history)
    
    total_new_events = 0
    
    for kw in new_kws:
        if kw in history: continue
        logging.info(f"--- 正在處理關鍵字: {kw} ---")
        history.append(kw)
        
        # 3. 搜索與爬取
        search_results = call_mcp_search(kw) or duckduckgo_html_search(kw)
        raw_events = []
        
        for res in search_results[:3]: # 每個關鍵字採集前 3 篇
            url = res.get('link') or res.get('url')
            crawled = await crawl_and_extract(url)
            if crawled and crawled.get('markdown'):
                # 本地歸納
                extracted = local_extract_events(crawled['markdown'])
                if extracted:
                    for e in extracted: e['link'] = url
                    raw_events.extend(extracted)
        
        # 4. 批量驗證 (按關鍵字批量)
        verified_events = verify_with_deepseek(raw_events)
        
        if verified_events:
            # 5. 向量去重與儲存
            events_to_save = []
            for e in verified_events:
                # 補全格式
                e['embedding'] = compute_embedding(f"{e['title']} {e['description']}")
                e['category'] = "auto_collected"
                e['verified'] = True
                e['updated'] = datetime.now().isoformat()
                events_to_save.append(e)
            
            save_events_to_db(events_to_save)
            total_new_events += len(events_to_save)
            print(f"  >> [進度] 關鍵字 '{kw}' 完成，新增/更新了 {len(events_to_save)} 個事件")

    # 更新歷史記錄
    with open(KEYWORDS_FILE, 'w') as f:
        json.dump(history, f)
    
    db_total = count_events_in_db()
    logging.info(f"循環結束。本次新增: {total_new_events}，目前資料庫總量: {db_total}")

if __name__ == "__main__":
    print("=== 2026 日曆資料自動採集器啟動 ===")
    while True:
        try:
            asyncio.run(run_cycle())
            print("正在等待下一輪 (600秒)...")
            time.sleep(600) # 每 10 分鐘跑一輪
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"循環發生異常: {e}")
            time.sleep(60)

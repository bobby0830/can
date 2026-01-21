import requests
import json
import re

# DeepSeek API 設定
DEEPSEEK_API_KEY = "sk-17696d9b237a48bf85ecbc6ea383f176"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"

def generate_expanded_queries(interests):
    """
    利用 DeepSeek 聯想與用戶興趣相關的專業搜尋詞。
    涵蓋大型會議、財務日、產品發布，以及小型技術活動（Webinars, Workshops, Community Calls）。
    """
    prompt = f"""
你是一個專業的搜尋專家。請根據用戶的興趣主題，生成 5 個精準的 2026 年相關活動搜尋關鍵字（英文）。
你的目標是全面覆蓋以下維度：
1. 財務/企業：財務報告 (Earnings)、股東大會 (Shareholder meetings)。
2. 產品/技術：產品發布 (Product Launches)、版本發布會 (Release Events)。
3. 社群/細節：網路研討會 (Webinars)、工作坊 (Workshops)、開發者日 (Developer Days)、社群時間 (Community/Builder Hours)。
4. 大型活動：技術大會 (Tech Conferences)、產業高峰會 (Summits)。

用戶興趣：{interests}

請僅回傳 JSON 陣列：
["query 1", "query 2", "query 3", "query 4", "query 5"]
"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一個精確的搜尋詞生成助手。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "response_format": {"type": "json_object"}
    }
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=20)
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        data = json.loads(content)
        if isinstance(data, list): return data
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list): return v
        return []
    except Exception as e:
        print(f"  [LLM] Query expansion failed: {e}")
        return []

def extract_events_from_text(text):
    """
    使用 DeepSeek API 從文本中簡單提取活動名稱。
    目標是「發現」活動，細節日期會在下一步驗證。
    """
    truncated_text = text[:10000] 
    prompt = f"""
請從下方的 Markdown 文本中提取 **2026 年提到的所有活動、會議、發布會或網路研討會**。

**提取準則：**
1. **簡單提取**：只要是 2026 年的活動就抓出來。
2. **日期處理**：有日期就寫 YYYY-MM-DD，沒有就寫 "2026-01-00"。
3. **忽略過去**：嚴格忽略 2025 年或更早的資訊。

輸出格式為 JSON 陣列，包含：
- "title": 活動名稱
- "date": "YYYY-MM-DD" 或 "2026-01-00"
- "description": 50字內簡介

Markdown 文本：
---
{truncated_text} 
---
"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一個專業的資料提取助手，只會輸出 JSON 格式。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "response_format": {"type": "json_object"} # DeepSeek 支援 JSON Mode
    }

    try:
        print(f"  [DeepSeek] Requesting extraction (Text len: {len(truncated_text)})...")
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 嘗試解析 JSON
        try:
            data = json.loads(content)
            # 處理 DeepSeek 可能將陣列包在物件裡的情況
            if isinstance(data, list):
                events = data
            elif isinstance(data, dict):
                events = []
                for key, value in data.items():
                    if isinstance(value, list):
                        events = value
                        break
                if not events and data:
                    # 如果 dict 只有一項且不是 list，可能就是單個事件
                    events = [data]
            else:
                events = []
                
            print(f"  [DeepSeek] Successfully extracted {len(events)} events.")
            return events
        except json.JSONDecodeError:
            # 嘗試用正則抓取 JSON 部分
            match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
            if match:
                events = json.loads(match.group(0))
                return events
            print(f"  [DeepSeek] Failed to parse JSON content: {content[:100]}...")
            return []

    except Exception as e:
        print(f"  [DeepSeek] Error calling API: {e}")
        return []

def refine_event_details(event_name, crawled_content):
    """
    針對特定事件的官網內容，進一步精煉日期和資訊。
    """
    prompt = f"""
請從下方的內容中，找出 "{event_name}" 在 2026 年的具體舉辦日期。
內容：
{crawled_content[:6000]}

請僅返回一個 JSON 物件：
{{
  "title": "{event_name}",
  "date": "精確日期",
  "description": "更新後的簡短描述"
}}
"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一個精確的資料提取助手。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except:
        return None

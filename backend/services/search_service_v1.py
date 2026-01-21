import requests
import json

SERPER_API_KEY = "d254221fb1ceb76ab6a9c724a8e5c1b1b0905507" # 已根據您的輸入更新

def is_likely_event(item):
    """
    判斷搜尋結果是否更像是一個事件而非論文。
    """
    title = item.get('title', '').lower()
    description = item.get('description', '').lower()
    text = f"{title} {description}"
    
    # 事件關鍵字
    event_keywords = ['conference', 'summit', 'workshop', 'expo', 'event', 'convention', 'forum', 'symposium', 'meetup', 'registration', 'agenda', 'speakers', 'venue']
    # 排除關鍵字 (論文相關)
    paper_keywords = ['paper', 'journal', 'doi:', 'abstract', 'citation', 'researchgate', 'arxiv', 'published in', 'author', 'manuscript']
    
    # 檢查是否包含事件詞
    has_event_kw = any(kw in text for kw in event_keywords)
    # 檢查是否包含排除詞
    has_paper_kw = any(kw in text for kw in paper_keywords)
    
    # 如果有事件詞且沒有明顯的論文特徵，則認為是事件
    return has_event_kw and not has_paper_kw

def search_events(query):
    """
    使用 Serper.dev 搜尋相關事件。
    優化搜尋詞以排除論文並增加活動關鍵字。
    """
    if SERPER_API_KEY == "YOUR_SERPER_API_KEY" or not SERPER_API_KEY:
        print("Warning: SERPER_API_KEY not set. Using mock data.")
        return get_mock_events(query)

    url = "https://google.serper.dev/search"
    # 優化搜尋詞：增加活動特徵詞，排除論文雜訊
    payload = json.dumps({
        "q": f"{query} (conference OR summit OR workshop OR expo OR event) 2026 -paper -journal -pdf -arxiv",
        "num": 15
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()
        
        events = []
        for result in results.get('organic', []):
            item = {
                'title': result.get('title'),
                'link': result.get('link'),
                'description': result.get('snippet')
            }
            
            # 層級過濾：1. 檢查是否像事件 2. 提取日期
            if is_likely_event(item):
                date_str = extract_date(item['description'] + item['title'])
                if date_str:
                    item['date'] = date_str
                    events.append(item)
                    
        return events
    except Exception as e:
        print(f"Error searching events: {e}")
        return get_mock_events(query)

import re

def extract_date(text):
    """
    從文本中提取日期。支援 YYYY-MM-DD, Month DD, YYYY 等格式。
    """
    # 模式 1: 2026-03-15
    iso_pattern = r'\b(2026)-(\d{1,2})-(\d{1,2})\b'
    # 模式 2: March 15, 2026 或 Mar 15 2026
    text_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})[,\s]+(2026)\b'
    
    # 嘗試 ISO 格式
    iso_match = re.search(iso_pattern, text)
    if iso_match:
        return f"{iso_match.group(1)}-{int(iso_match.group(2)):02d}-{int(iso_match.group(3)):02d}"
    
    # 嘗試文字格式
    text_match = re.search(text_pattern, text, re.IGNORECASE)
    if text_match:
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        month_str = text_match.group(1).lower()[:3]
        month = months.get(month_str, 1)
        day = int(text_match.group(2))
        year = text_match.group(3)
        return f"{year}-{month:02d}-{day:02d}"
    
    return None

def get_mock_events(query):
    """返回與科技相關的模擬事件"""
    return [
        {
            "title": "AI Summit 2026",
            "link": "https://example.com/ai-summit",
            "description": "The biggest AI conference of the year focusing on LLMs and robotics.",
            "date": "2026-05-20"
        },
        {
            "title": "Flutter World Congress",
            "link": "https://example.com/flutter-world",
            "description": "Join developers worldwide to discuss the future of Flutter and Dart.",
            "date": "2026-08-15"
        },
        {
            "title": "TechCrunch Disrupt 2026",
            "link": "https://example.com/disrupt",
            "description": "Where startups and investors meet to shape the future of technology.",
            "date": "2026-10-05"
        }
    ]


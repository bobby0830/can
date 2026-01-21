import asyncio
import requests
import re
import json
from services.mcp_wrapper import call_mcp_search
from services.crawler_utils import crawl_and_extract
from services.llm_service import extract_events_from_text, refine_event_details, generate_expanded_queries
from services.db_service import save_events_to_db
from services.recommender import compute_embedding

def duckduckgo_html_search(query):
    """備案搜尋"""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": f"{query} 2026"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        links = re.findall(r'result__a"\s+href="([^"]+)"', response.text)
        titles = re.findall(r'result__a"[^>]+>([^<]+)</a>', response.text)
        return [{"title": titles[i].strip(), "link": links[i]} for i in range(min(len(links), 5))]
    except: return []

def search_events(query):
    """
    推薦系統 v7：兩階段策略 (發現列表 -> 官網驗證)。
    """
    search_query = query.replace("機器學習", "Machine Learning").replace("人工智慧", "AI")
    print(f"\n[DEBUG] === 兩階段搜尋開始: {search_query} ===", flush=True)
    
    # 策略 1：找「推薦清單」與「官網活動頁」
    discovery_queries = [
        f"best {search_query} events conferences 2026 list",  # 找推薦文章
        f"{search_query} official events calendar 2026",     # 找官方日曆
        f"{search_query} news releases blog 2026"            # 找最新公告
    ]
    
    all_raw_results = []
    seen_urls = set()
    for q in discovery_queries:
        print(f"[DEBUG] 發現層搜尋: {q}")
        results = call_mcp_search(q) or duckduckgo_html_search(q)
        for r in results:
            url = r.get('link') or r.get('url')
            if url and url not in seen_urls:
                if "2025" in r.get('title', '').lower() and "2026" not in r.get('title', ''): continue
                seen_urls.add(url)
                all_raw_results.append(r)

    if not all_raw_results: return []
        
    all_extracted_events = {} 
    loop = asyncio.get_event_loop()
    
    # 策略 2：從文章中提取「活動名稱」
    for res in all_raw_results[:6]: # 讀取前 6 篇最相關的文章
        url = res.get('link') or res.get('url')
        print(f"[DEBUG] 正在從文章提取活動: {url}")
        crawled_data = loop.run_until_complete(crawl_and_extract(url))
        if crawled_data and crawled_data.get('markdown'):
            found = extract_events_from_text(crawled_data['markdown'])
            for event in found:
                name = event.get('title')
                if name and len(name) > 3:
                    all_extracted_events[name] = event

    # 策略 3：針對拿到的活動，進行「官網日期驗證」
    # 挑選前 5 個最有潛力的活動（尤其是日期不詳的）
    verification_targets = list(all_extracted_events.values())[:5]
    for event in verification_targets:
        if event.get('date') == '2026-01-00':
            refine_q = f"{event['title']} official website 2026 date"
            print(f"[DEBUG] 驗證層：正在尋找 {event['title']} 的確切日期...")
            v_results = call_mcp_search(refine_q) or duckduckgo_html_search(refine_q)
            if v_results:
                v_url = v_results[0].get('link') or v_results[0].get('url')
                v_data = loop.run_until_complete(crawl_and_extract(v_url))
                if v_data and v_data.get('markdown'):
                    refined = refine_event_details(event['title'], v_data['markdown'])
                    try:
                        r_json = json.loads(refined)
                        if r_json.get('date') and r_json.get('date') != '2026-01-00':
                            event['date'] = r_json['date']
                            event['link'] = v_url # 更新為官方連結
                    except: pass

    # 4. 向量化與存檔
    final_list = []
    for name, event in all_extracted_events.items():
        # 計算向量用於去重與推薦
        emb = compute_embedding(f"{name} {event.get('description', '')}")
        event['embedding'] = emb
        final_list.append(event)
    
    if final_list:
        save_events_to_db(final_list)

    return final_list

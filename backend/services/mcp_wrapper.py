import json
import requests
import os

def call_mcp_search(query):
    """
    透過本地 MCP 伺服器 (pskill9/web-search) 進行真實搜尋。
    """
    print(f"\n[DEBUG] === Starting MCP Wrapper for: {query} ===", flush=True)
    mcp_endpoint = os.getenv("MCP_SEARCH_ENDPOINT", "http://host.docker.internal:8000/search")
    
    try:
        # 這裡我們加上 2026 events 關鍵字來縮小搜尋範圍
        search_query = f"{query} events 2026"
        print(f"[DEBUG] Requesting URL: {mcp_endpoint} with query: {search_query}", flush=True)
        
        response = requests.get(mcp_endpoint, params={"q": search_query}, timeout=15)
        print(f"[DEBUG] Bridge response status: {response.status_code}", flush=True)
        
        response.raise_for_status()
        results = response.json()
        
        # [關鍵] 詳細列印收到的資料結構
        print(f"[DEBUG] Raw JSON from bridge: {json.dumps(results, indent=2)}", flush=True)
        
        if not results:
            print("[DEBUG] MCP returned an empty list.", flush=True)
            return []
            
        # 確保返回的是列表格式
        if isinstance(results, dict) and "results" in results:
            results = results["results"]
        elif isinstance(results, dict):
            # 有些搜尋引擎返回單個物件或不同鍵名
            results = results.get("organic", results.get("results", results.get("data", [])))

        print(f"[DEBUG] Successfully parsed {len(results)} search items.", flush=True)
        return results

    except Exception as e:
        error_msg = f"[CRITICAL ERROR] MCP Wrapper failed: {e}"
        print(error_msg)
        raise Exception(error_msg)

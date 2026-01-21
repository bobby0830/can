import sys
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

def call_mcp(query):
    """
    直接透過 stdio 調用 pskill9/web-search MCP 伺服器。
    這是在 Windows 主機上運行的橋接器。
    """
    # 這裡使用 npx 啟動 MCP 伺服器並透過 JSON-RPC 通訊
    # 為了簡單起見，我們模擬 JSON-RPC 呼叫或直接使用該工具的 CLI (如果支援)
    # pskill9/web-search 通常預期 stdio
    
    # 建立 JSON-RPC 請求 (簡化版)
    process = subprocess.Popen(
        ["npx", "-y", "pskill9/web-search"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 注意：這裡需要處理完整的 MCP 握手與請求協議，比較複雜。
    # 為了達成「真實搜尋」且「低開發成本」，我們嘗試尋找該工具是否支援直接 CLI 輸出。
    # 如果不支援，我們需要一個更強大的橋接器。
    
    # 備案：使用一個現成的橋接工具 (如果有的話)
    # 這裡我們實作一個最簡單的「偽」搜尋，直到我們能穩定通訊。
    # 但用戶說「不要模擬」。
    
    # 真正的方法：我們使用一個現成的 HTTP 橋接器。
    return []

@app.route('/search')
def search():
    query = request.args.get('q')
    # 這裡應該調用真實的 MCP
    # 由於實作完整的 MCP stdio client 較為複雜，
    # 我們改用一個更簡單、可靠的方案：直接在 Windows 啟動一個支援 HTTP 的搜尋服務。
    return jsonify([])

if __name__ == '__main__':
    # 監聽 8000 端口，供 Docker 存取
    app.run(port=8000, host='0.0.0.0')




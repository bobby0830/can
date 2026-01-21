# 2026 個人化智能日曆推薦系統 (AI Calendar Suggest System)

這是一個基於 AI 的智能日曆系統，能夠自動從網路爬取、分析並驗證 2026 年的全球活動（如科技大會、財務報表日、產品發布會等），並根據用戶興趣提供個人化推薦。

## 🌟 核心功能

*   **智能搜尋與擴展**：利用 DeepSeek API 自動將用戶興趣（如 "NVDA"）聯想為專業搜尋關鍵字。
*   **兩階段發現驗證**：先從推薦文章中發現活動名稱，再自動定位官網驗證精確日期。
*   **本地 LLM 採集 (Ollama)**：背景自動運行腳本，利用本地模型降低採集成本。
*   **向量去重**：使用 Sentence-Transformers 進行語義比對，自動合併重複活動。
*   **離線緩存**：預先建立事件資料庫，實現秒級響應的離線推薦。

## 🛠️ 技術棧

*   **後端**: Python Flask, SQLite
*   **前端**: Flutter (Mobile/Desktop)
*   **AI/LLM**: DeepSeek API, Ollama (本地), Sentence-Transformers
*   **爬蟲**: Crawl4AI, MCP Web Search
*   **容器化**: Docker & Docker Compose

## 🚀 快速開始

### 1. 環境準備
*   安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   安裝 [Ollama](https://ollama.com/) 並運行 `ollama run llama3`
*   獲取 [DeepSeek API Key](https://platform.deepseek.com/)

### 2. 配置 API Key
在 `backend/services/llm_service.py` 中填入您的 `DEEPSEEK_API_KEY`。

### 3. 一鍵啟動 (Windows)
雙擊運行根目錄下的：
```bash
start_app.bat
```
這將自動啟動後端 Docker 容器及 Flutter 前端介面。

### 4. 啟動背景自動採集器
如果您希望系統自動在後台擴充資料庫，請在後端目錄運行：
```bash
python background_worker.py
```

## 📂 專案結構
*   `/backend`: Flask API 服務、資料庫管理、AI 邏輯。
*   `/frontend`: Flutter 用戶介面。
*   `mcp_bridge.js`: 模擬 Google 搜尋的橋接工具。
*   `background_worker.py`: 本地離線採集腳本。

## 📝 使用說明
1.  啟動 App 後，在問卷頁面輸入您的感興趣的關鍵字（如：AI, US Finance, NVDA）。
2.  系統會自動檢查資料庫，若相關活動不足，將觸發即時網路搜尋。
3.  切換至日曆頁面即可查看推薦的 2026 年活動。

# 使用官方 Python 輕量版作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (sentence-transformers 需要一些編譯工具)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件並安裝
COPY requirements.txt .
# 使用 cache mount 加速安裝，避免每次都重新下載
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# 預先下載 NLP 模型
RUN --mount=type=cache,target=/root/.cache/torch \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 安裝 Playwright 所需的瀏覽器 (v2 版本必需)
RUN playwright install chromium --with-deps

# 複製所有後端程式碼
COPY . .

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露 5000 端口
EXPOSE 5000

# 啟動應用程式
CMD ["flask", "run"]

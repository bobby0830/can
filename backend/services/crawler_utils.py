import asyncio
from crawl4ai import AsyncWebCrawler
import re
import sys
import io

# 解決 Windows 下的編碼問題
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def crawl_and_extract(url):
    """
    使用 Crawl4AI 爬取網頁內容並回傳 Markdown 供 LLM 處理。
    """
    print(f"  [Crawler] Accessing {url}...")
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url)
            
            if not result or not result.success:
                print(f"  [Crawler] Failed to fetch content from {url}")
                return None

            # 獲取 Markdown 內容
            markdown_content = result.markdown if result.markdown else ""
            print(f"  [Crawler] Content length: {len(markdown_content)} characters")
            
            # 回傳完整內容，讓 LLM 決定是否為事件
            return {
                "title": result.metadata.get('title', 'Unknown') if result.metadata else "Unknown",
                "markdown": markdown_content,
                "url": url
            }
    except Exception as e:
        print(f"  [Crawler] Error during extraction: {e}")
        return None

if __name__ == "__main__":
    # 測試程式
    test_url = "https://example.com"
    asyncio.run(crawl_and_extract(test_url))


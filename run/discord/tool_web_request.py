import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.chunking_strategy import SlidingWindowChunking


async def make_web_request(url: str, method: str, body: str, headers: dict):
    """
    Make a web request using the AsyncWebCrawler class
    """
    async with AsyncWebCrawler(
        headless=True,           # Run in headless mode (no GUI)
        verbose=True,           # Enable detailed logging
        sleep_on_close=False    # No delay when closing browser
    ) as crawler:
        result = await crawler.arun(url=url, method=method, body=body, headers=headers)

        large_text = result.markdown

        chunker = SlidingWindowChunking(window_size=100, step=50)
        window_chunks = chunker.chunk(large_text)

        return {
            "url": url,
            "method": method,
            "result": window_chunks
        }
    
import httpx
from datetime import datetime
from domain.interfaces import WebCrawler
from domain.models import WebPage

class HttpWebCrawler(WebCrawler):
    """Implementation of WebCrawler using httpx"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True
        )
    
    async def crawl(self, url: str) -> WebPage:
        """Crawl a web page and return its raw HTML content"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return WebPage(
                url=url,
                raw_html=response.text,
                crawled_at=datetime.now()
            )
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to crawl {url}: {str(e)}")
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

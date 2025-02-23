import httpx
from datetime import datetime
from typing import Dict
from domain.interfaces import WebCrawler
from domain.models import WebPage

class HttpWebCrawler(WebCrawler):
    """Implementation of WebCrawler using httpx"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=self.headers
        )
    
    async def crawl(self, url: str) -> WebPage:
        """Crawl a web page and return its raw HTML content"""
        try:
            # First try with default headers
            response = await self.client.get(url)
            
            # If we get a 403, try with additional site-specific headers
            if response.status_code == 403 and 'brokerchooser.com' in url:
                # Add specific headers for brokerchooser.com
                site_headers = self.headers.copy()
                site_headers.update({
                    'Referer': 'https://brokerchooser.com/',
                    'Origin': 'https://brokerchooser.com'
                })
                
                response = await self.client.get(url, headers=site_headers)
            
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

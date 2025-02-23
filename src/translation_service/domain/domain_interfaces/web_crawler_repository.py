from abc import ABC, abstractmethod
from domain.model.web_page import WebPage

class WebCrawlerRepository(ABC):
    """Interface for web page crawling"""
    @abstractmethod
    async def crawl(self, url: str) -> WebPage:
        """Crawl a web page and return its content"""
        pass

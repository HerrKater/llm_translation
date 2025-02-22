from abc import ABC, abstractmethod
from .models import WebPage, TranslationRequest, Translation

class WebCrawler(ABC):
    """Interface for web page crawling"""
    @abstractmethod
    async def crawl(self, url: str) -> WebPage:
        """Crawl a web page and return its content"""
        pass

class ContentProcessor(ABC):
    """Interface for processing web page content"""
    @abstractmethod
    async def process(self, webpage: WebPage) -> WebPage:
        """Process the web page content and return processed content"""
        pass

class Translator(ABC):
    """Interface for translation service"""
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> Translation:
        """Translate content into multiple languages"""
        pass

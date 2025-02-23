from abc import ABC, abstractmethod
from domain.model.web_page import WebPage

class ContentProcessor(ABC):
    """Interface for processing web page content"""
    @abstractmethod
    async def process(self, webpage: WebPage) -> WebPage:
        """Process the web page content and return processed content"""
        pass

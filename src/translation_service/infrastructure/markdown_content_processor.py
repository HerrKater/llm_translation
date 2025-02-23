from markdownify import markdownify as md
from bs4 import BeautifulSoup
from domain.infrastructure_interfaces.content_processor import ContentProcessor
from domain.model.web_page import WebPage

class MarkdownContentProcessor(ContentProcessor):
    """Implementation of ContentProcessor using markdownify"""
    
    def __init__(self):
        pass
    
    async def process(self, webpage: WebPage) -> WebPage:
        """Process HTML content and convert it to markdown"""
        try:
            # Clean HTML first
            soup = BeautifulSoup(webpage.raw_html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            # Convert to markdown using markdownify
            webpage.markdown_content = md(str(soup))
            
            return webpage
        except Exception as e:
            raise ValueError(f"Failed to process content: {str(e)}")

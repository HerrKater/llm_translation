import html2text
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
from domain.interfaces import ContentProcessor
from domain.models import WebPage

class MarkdownContentProcessor(ContentProcessor):
    """Implementation of ContentProcessor using html2text and markdown-it-py"""
    
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.ignore_images = False
        self.html2text.body_width = 0  # No wrapping
        self.html2text.protect_links = True
        self.markdown = MarkdownIt()
    
    async def process(self, webpage: WebPage) -> WebPage:
        """Process HTML content and convert it to markdown"""
        try:
            # Clean HTML first
            soup = BeautifulSoup(webpage.raw_html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            # Convert to markdown while preserving structure
            markdown = self.html2text.handle(str(soup))
            
            # Validate markdown by parsing and re-rendering
            # This ensures we have valid markdown syntax
            ast = self.markdown.parse(markdown)
            webpage.markdown_content = self.markdown.render(ast)
            
            return webpage
        except Exception as e:
            raise ValueError(f"Failed to process content: {str(e)}")

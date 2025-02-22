from typing import List
from domain.interfaces import WebCrawler, ContentProcessor, Translator
from domain.models import TranslationRequest, Translation, WebPage

class TranslationService:
    """Application service that orchestrates the translation process"""
    
    def __init__(
        self,
        crawler: WebCrawler,
        processor: ContentProcessor,
        translator: Translator
    ):
        self.crawler = crawler
        self.processor = processor
        self.translator = translator
    
    async def translate_webpage(
        self,
        url: str,
        target_languages: List[str]
    ) -> Translation:
        """
        Orchestrates the complete webpage translation process:
        1. Crawls the webpage
        2. Processes the HTML to markdown
        3. Translates the content
        """
        # Crawl webpage
        webpage: WebPage = await self.crawler.crawl(url)
        
        # Process content
        processed_webpage: WebPage = await self.processor.process(webpage)
        if not processed_webpage.markdown_content:
            raise ValueError("Failed to process webpage content")
        
        # Create translation request
        request = TranslationRequest(
            source_content=processed_webpage.markdown_content,
            target_languages=target_languages
        )
        
        # Translate content
        return await self.translator.translate(request)

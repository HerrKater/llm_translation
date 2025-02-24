from typing import List
from domain.domain_interfaces.web_crawler_repository import WebCrawlerRepository
from domain.domain_interfaces.content_processor import ContentProcessor
from domain.domain_interfaces.translator_service import TranslatorService
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation
from domain.model.web_page import WebPage

class TranslationOrchestrator:
    """Application service that orchestrates the translation process"""
    
    def __init__(
        self,
        crawler: WebCrawlerRepository,
        processor: ContentProcessor,
        translator: TranslatorService
    ):
        self.crawler = crawler
        self.processor = processor
        self.translator = translator
    
    async def translate_webpage(
        self,
        url: str,
        target_languages: List[str]
    ) -> tuple[Translation, dict]:
        """
        Orchestrates the complete webpage translation process:
        1. Crawls the webpage
        2. Processes the HTML to markdown
        3. Translates the content
        
        Returns:
            tuple containing:
            - Translation object
            - Cost information dictionary
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
        
        # Translate content and get cost info
        return await self.translator.translate(request)

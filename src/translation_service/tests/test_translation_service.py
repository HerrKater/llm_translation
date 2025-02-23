import pytest
from datetime import datetime
from domain.model.web_page import WebPage
from domain.model.translation import Translation
from domain.domain_interfaces.web_crawler_repository import WebCrawlerRepository
from domain.domain_interfaces.content_processor import ContentProcessor
from domain.domain_interfaces.translator_service import TranslatorService
from application.translation_service import TranslationOrchestrator

class MockWebCrawler(WebCrawlerRepository):
    async def crawl(self, url: str) -> WebPage:
        return WebPage(
            url=url,
            raw_html="<html><body><h1>Test</h1><p>Content</p></body></html>",
            crawled_at=datetime.now()
        )

class MockContentProcessor(ContentProcessor):
    async def process(self, webpage: WebPage) -> WebPage:
        webpage.markdown_content = "# Test\nContent"
        return webpage

class MockTranslator(TranslatorService):
    async def translate(self, request) -> Translation:
        return Translation(
            original_content=request.source_content,
            translations={"Spanish": "# Prueba\nContenido"}
        )

@pytest.fixture
def translation_orchestrator():
    return TranslationService(
        MockWebCrawler(),
        MockContentProcessor(),
        MockTranslator()
    )

@pytest.mark.asyncio
async def test_translate_webpage(translation_orchestrator):
    # Arrange
    url = "https://example.com"
    target_languages = ["Spanish"]
    
    # Act
    result = await translation_orchestrator.translate_webpage(url, target_languages)
    
    # Assert
    assert result.original_content == "# Test\nContent"
    assert "Spanish" in result.translations
    assert result.translations["Spanish"] == "# Prueba\nContenido"

import pytest
from datetime import datetime
from domain.models import WebPage, Translation
from domain.interfaces import WebCrawler, ContentProcessor, Translator
from application.translation_service import TranslationService

class MockWebCrawler(WebCrawler):
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

class MockTranslator(Translator):
    async def translate(self, request) -> Translation:
        return Translation(
            original_content=request.source_content,
            translations={"Spanish": "# Prueba\nContenido"}
        )

@pytest.fixture
def translation_service():
    return TranslationService(
        MockWebCrawler(),
        MockContentProcessor(),
        MockTranslator()
    )

@pytest.mark.asyncio
async def test_translate_webpage(translation_service):
    # Arrange
    url = "https://example.com"
    target_languages = ["Spanish"]
    
    # Act
    result = await translation_service.translate_webpage(url, target_languages)
    
    # Assert
    assert result.original_content == "# Test\nContent"
    assert "Spanish" in result.translations
    assert result.translations["Spanish"] == "# Prueba\nContenido"

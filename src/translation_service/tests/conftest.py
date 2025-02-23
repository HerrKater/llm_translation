import pytest
from domain.model.web_page import WebPage
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation
from infrastructure.config import Settings
from datetime import datetime

@pytest.fixture
def settings():
    """Test settings with mock values"""
    return Settings(
        openai_api_key="test-key",
        openai_url="https://test.openai.com",
        language_model="test-model"
    )

@pytest.fixture
def mock_webpage():
    """Sample webpage for testing"""
    return WebPage(
        url="https://test.com",
        raw_html="<html><body><h1>Test</h1></body></html>",
        markdown_content="# Test",
        crawled_at=datetime.now()
    )

@pytest.fixture
def mock_translation_request():
    """Sample translation request for testing"""
    return TranslationRequest(
        source_content="Hello world",
        target_languages=["hu", "es"]
    )

@pytest.fixture
def mock_translation():
    """Sample translation result for testing"""
    return Translation(
        original_content="Hello world",
        translations={
            "hu": "Helló világ",
            "es": "Hola mundo"
        }
    )

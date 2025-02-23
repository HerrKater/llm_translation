import pytest
from domain.domain_interfaces.content_processor import ContentProcessor
from domain.model.web_page import WebPage

@pytest.mark.asyncio
class TestContentProcessor:
    @pytest.fixture
    def content_processor(self):
        return ContentProcessor()
    
    async def test_process_html_to_markdown(self, content_processor, mock_webpage):
        # Setup
        mock_webpage.raw_html = "<h1>Test</h1><p>Hello world</p>"
        
        # Execute
        result = await content_processor.process(mock_webpage)
        
        # Verify
        assert isinstance(result, WebPage)
        assert result.markdown_content is not None
        assert "# Test" in result.markdown_content
        assert "Hello world" in result.markdown_content
    
    async def test_process_preserves_original_fields(self, content_processor, mock_webpage):
        # Execute
        result = await content_processor.process(mock_webpage)
        
        # Verify
        assert result.url == mock_webpage.url
        assert result.raw_html == mock_webpage.raw_html
        assert result.crawled_at == mock_webpage.crawled_at

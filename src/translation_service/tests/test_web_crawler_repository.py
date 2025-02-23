import pytest
from unittest.mock import Mock, patch
from domain.domain_interfaces.web_crawler_repository import WebCrawlerRepository
from domain.model.web_page import WebPage

@pytest.mark.asyncio
class TestWebCrawlerRepository:
    @pytest.fixture
    def mock_http_client(self):
        return Mock()
    
    @pytest.fixture
    def crawler_repository(self, mock_http_client):
        with patch('domain.services.web_crawler_repository.httpx.AsyncClient', return_value=mock_http_client):
            return WebCrawlerRepository()
    
    async def test_crawl_success(self, crawler_repository, mock_http_client):
        # Setup
        url = "https://test.com"
        mock_response = Mock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_http_client.get.return_value = mock_response
        
        # Execute
        result = await crawler_repository.crawl(url)
        
        # Verify
        assert isinstance(result, WebPage)
        assert result.url == url
        assert result.raw_html == mock_response.text
        mock_http_client.get.assert_called_once_with(url)
    
    async def test_crawl_http_error(self, crawler_repository, mock_http_client):
        # Setup
        url = "https://test.com"
        mock_http_client.get.side_effect = Exception("HTTP Error")
        
        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            await crawler_repository.crawl(url)
        assert "Failed to crawl" in str(exc_info.value)

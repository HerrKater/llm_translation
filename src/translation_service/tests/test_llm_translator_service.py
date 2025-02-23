import pytest
from unittest.mock import Mock, patch
from domain.services.llm_translator import LlmTranslatorService
from domain.model.translation import Translation

@pytest.mark.asyncio
class TestLlmTranslatorService:
    @pytest.fixture
    def mock_llm_client(self):
        return Mock()
    
    @pytest.fixture
    def translator_service(self, settings, mock_llm_client):
        with patch('domain.services.llm_translator_service.create_llm_client', return_value=mock_llm_client):
            return LlmTranslatorService(settings)
    
    async def test_translate_success(self, translator_service, mock_llm_client, mock_translation_request):
        # Setup
        mock_llm_client.chat.return_value = "Translated text"
        
        # Execute
        result = await translator_service.translate(mock_translation_request)
        
        # Verify
        assert isinstance(result, Translation)
        assert result.original_content == mock_translation_request.source_content
        assert len(result.translations) == len(mock_translation_request.target_languages)
        assert all(lang in result.translations for lang in mock_translation_request.target_languages)
        assert mock_llm_client.chat.call_count == len(mock_translation_request.target_languages)
    
    async def test_translate_error(self, translator_service, mock_llm_client, mock_translation_request):
        # Setup
        mock_llm_client.chat.side_effect = Exception("API Error")
        
        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            await translator_service.translate(mock_translation_request)
        assert "Translation failed" in str(exc_info.value)

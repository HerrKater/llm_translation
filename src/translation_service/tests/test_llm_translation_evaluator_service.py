import pytest
import json
from unittest.mock import Mock, patch
from domain.services.llm_translation_evaluator import LlmTranslationEvaluatorService
from domain.domain_interfaces.translation_evaluator import TranslationEvaluationResult

@pytest.mark.asyncio
class TestLlmTranslationEvaluatorService:
    @pytest.fixture
    def mock_llm_client(self):
        return Mock()
    
    @pytest.fixture
    def evaluator_service(self, settings, mock_llm_client):
        with patch('domain.services.llm_translation_evaluator_service.create_llm_client', return_value=mock_llm_client):
            return LlmTranslationEvaluatorService(settings)
    
    @pytest.fixture
    def mock_evaluation_response(self):
        return json.dumps({
            "accuracy_score": 8.5,
            "fluency_score": 9.0,
            "matches_reference": True,
            "comments": "Excellent translation"
        })
    
    async def test_evaluate_translation_success(self, evaluator_service, mock_llm_client, mock_evaluation_response):
        # Setup
        mock_llm_client.chat.return_value = mock_evaluation_response
        
        # Execute
        result = await evaluator_service.evaluate_translation(
            english_text="Hello",
            reference_translation="Helló",
            new_translation="Helló"
        )
        
        # Verify
        assert isinstance(result, TranslationEvaluationResult)
        assert result.accuracy_score == 8.5
        assert result.fluency_score == 9.0
        assert result.matches_reference is True
        assert result.comments == "Excellent translation"
        assert mock_llm_client.chat.call_count == 1
    
    async def test_evaluate_translation_invalid_response(self, evaluator_service, mock_llm_client):
        # Setup
        mock_llm_client.chat.return_value = "Invalid JSON"
        
        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            await evaluator_service.evaluate_translation(
                english_text="Hello",
                reference_translation="Helló",
                new_translation="Helló"
            )
        assert "Failed to parse evaluation response" in str(exc_info.value)

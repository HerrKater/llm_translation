from typing import Dict, Tuple
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation
from domain.model.settings import Settings
from domain.model.llm_pricing import LLMPricing
from infrastructure.llm.factory import create_llm_client
from domain.domain_interfaces.translator_service import TranslatorService
from domain.model.settings import LLMProvider
from domain.services.translation_system import TranslationSystem

class LlmTranslatorService(TranslatorService):
    """Implementation of Translator using OpenAI's API"""
    
    def __init__(self, settings: Settings):
        self.llm_client = create_llm_client(
            provider=LLMProvider.OPENAI,
            settings=settings
        )
        self.translation_system = TranslationSystem()

    async def translate(self, request: TranslationRequest, model: str) -> Tuple[Translation, Dict]:
        # Use provided model or fallback to default
        """Translate content into multiple languages using OpenAI and track costs"""
        translations: Dict[str, str] = {}
        total_input_tokens = 0
        total_output_tokens = 0
        
        for language in request.target_languages:
            try:
                system_prompt = self.translation_system.get_translation_prompt(language)
                
                # Call LLM and get response with usage info
                response = await self.llm_client.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"\n\nTranslate the following text:\n\n{request.source_content}"}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                translations[language] = response['content']
                
                # Track token usage
                total_input_tokens += response['usage']['prompt_tokens']
                total_output_tokens += response['usage']['completion_tokens']
                
            except Exception as e:
                raise ValueError(f"Translation failed for {language}: {str(e)}")
        
        # Calculate cost
        total_cost, cost_breakdown = LLMPricing.calculate_cost(
            model=model,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens
        )
        
        # Add model information to cost breakdown
        cost_breakdown['model'] = model
        
        return Translation(
            original_content=request.source_content,
            translations=translations
        ), cost_breakdown

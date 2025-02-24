from typing import Dict, Tuple
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation
from domain.model.settings import Settings
from domain.model.llm_pricing import LLMPricing
from infrastructure.llm.factory import create_llm_client
from domain.domain_interfaces.translator_service import TranslatorService

class LlmTranslatorService(TranslatorService):
    """Implementation of Translator using OpenAI's API"""
    
    def __init__(self, settings: Settings):
        self.llm_client = create_llm_client(
            provider=settings.llm_provider,
            settings=settings
        )
        self.model = settings.language_model

    async def translate(self, request: TranslationRequest, model: str = None) -> Tuple[Translation, Dict]:
        # Use provided model or fallback to default
        model_to_use = model or self.model
        """Translate content into multiple languages using OpenAI and track costs"""
        translations: Dict[str, str] = {}
        total_input_tokens = 0
        total_output_tokens = 0
        
        for language in request.target_languages:
            try:
                system_prompt = (
                    f"You are a professional translator. Translate the following "
                    f"markdown content into {language}. Follow these rules strictly:\n"
                    f"1. Maintain all original structure, formatting, and markdown syntax\n"
                    f"2. DO NOT translate any text inside square brackets (e.g. [brokerName])\n"
                    f"3. Ensure the translation sounds natural in {language}\n"
                    f"4. Keep all placeholders exactly as they appear in the original text"
                )
                
                # Call LLM and get response with usage info
                response = self.llm_client.chat(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.source_content}
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
            model=self.model,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens
        )
        
        # Add model information to cost breakdown
        cost_breakdown['model'] = self.model
        
        return Translation(
            original_content=request.source_content,
            translations=translations
        ), cost_breakdown

import openai
import httpx
from typing import Dict
from domain.interfaces import Translator
from domain.models import TranslationRequest, Translation
from infrastructure.config import Settings

class OpenAITranslator(Translator):
    """Implementation of Translator using OpenAI's API"""
    
    def __init__(self, settings: Settings):
        self.client = openai.AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.url,
            default_headers={"api-version": settings.api_version},
            http_client=httpx.AsyncClient(
                base_url=settings.url,
                headers={"api-version": settings.api_version}
            )
        )
        self.model = settings.language_model

    async def translate(self, request: TranslationRequest) -> Translation:
        """Translate content into multiple languages using OpenAI"""
        translations: Dict[str, str] = {}
        
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
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.source_content}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                translations[language] = response.choices[0].message.content
                
            except Exception as e:
                raise ValueError(f"Translation failed for {language}: {str(e)}")
        
        return Translation(
            original_content=request.source_content,
            translations=translations
        )

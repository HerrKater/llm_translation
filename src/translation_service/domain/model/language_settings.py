from typing import List, Dict
from pydantic import BaseModel

class LanguageConfig(BaseModel):
    """Configuration for a supported language"""
    code: str
    name: str

class LanguageSettings(BaseModel):
    """Settings for supported languages"""
    supported_languages: List[LanguageConfig] = [
        LanguageConfig(code="es", name="Spanish"),
        LanguageConfig(code="fr", name="French"),
        LanguageConfig(code="de", name="German"),
        LanguageConfig(code="ja", name="Japanese"),
        LanguageConfig(code="ar", name="Arabic"),
        LanguageConfig(code="hi", name="Hindi"),
        LanguageConfig(code="pt", name="Portuguese"),
        LanguageConfig(code="hu", name="Hungarian")
    ]

    def get_language_codes(self) -> List[str]:
        """Get list of supported language codes"""
        return [lang.code for lang in self.supported_languages]

    def get_language_names(self) -> Dict[str, str]:
        """Get mapping of language codes to names"""
        return {lang.code: lang.name for lang in self.supported_languages}

    def is_language_supported(self, code: str) -> bool:
        """Check if a language code is supported"""
        return code in self.get_language_codes()

# Create a singleton instance
language_settings = LanguageSettings()

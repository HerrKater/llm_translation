"""
Language-specific translation rules architecture.

This module implements a flexible system for managing language-specific translation rules:
1. A base abstract class `TranslationRules` defining the interface for all language-specific rules
2. Concrete implementations for Hungarian and German language rules
3. A factory pattern (`TranslationRulesFactory`) to manage and retrieve language rules

The architecture allows for:
- Easy addition of new language-specific rules
- Clear separation of concerns
- Consistent interface for all language rules
- Flexible lookup by either language code or full name
- Reusable rule components for both translation and evaluation

To add a new language:
1. Create a new class that inherits from `TranslationRules`
2. Implement the required methods and properties
3. Register it with the factory
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict


class TranslationRules(ABC):
    """
    Base class for language-specific translation rules.
    This class defines the interface for language rule implementations.
    """
    
    @abstractmethod
    def get_rules(self) -> str:
        """
        Returns the language-specific rules as a formatted string.
        
        Returns:
            str: Formatted string containing translation rules
        """
        pass
    
    @abstractmethod
    def get_translation_examples(self) -> Optional[str]:
        """
        Returns examples of correct translations for this language.
        
        Returns:
            Optional[str]: Formatted string with translation examples or None if not applicable
        """
        pass
    
    @abstractmethod
    def get_evaluation_examples(self) -> Optional[str]:
        """
        Returns fewshot examples for translation evaluation for this language.
        
        Returns:
            Optional[str]: Formatted string with evaluation examples or None if not applicable
        """
        pass
    
    @property
    @abstractmethod
    def language_code(self) -> str:
        """
        Returns the language code for this rule set.
        
        Returns:
            str: Language code (e.g., "hu" for Hungarian)
        """
        pass
        
    @property
    @abstractmethod
    def language_name(self) -> str:
        """
        Returns the language name for this rule set.
        
        Returns:
            str: Language name (e.g., "Hungarian")
        """
        pass


class HungarianTranslationRules(TranslationRules):
    """
    Hungarian-specific translation rules implementation.
    """
    
    @property
    def language_code(self) -> str:
        return "hu"
    
    @property
    def language_name(self) -> str:
        return "Hungarian"
    
    def get_rules(self) -> str:
        """
        Returns Hungarian-specific translation rules.
        """
        return """
Hungarian Translation Guidelines:

1. Quantity + Singular Noun Rule: 
   - Nouns preceded by numerals or quantity expressions ALWAYS remain in the singular form
   - Example: "5 books" → "5 könyv" (NOT "5 könyvek")
   - Example: "several parameters" → "több paraméter" (NOT "több paraméterek")

2. Parameter Integration:
   - When a parameter represents a quantity (like [dataPoints]+), the following noun should be singular
   - Example: "across [dataPoints]+ criteria" → "[dataPoints]+ kritérium mentén"

3. "To" Preposition Translations:
   - "Alternatives to X" → "Alternatívák X helyett" (using "helyett" meaning "instead of")
   - NOT "Alternatívák az X számára" (which means "Alternatives for X" - a different meaning)
   - "Solution to X" → "X megoldása" (possessive construction)
   - "Guide to X" → "Útmutató az X-hez" (using -hez/-hoz/-höz allative case)

4. Common Patterns:
   - "X compared to Y" → "X Y-hoz képest" (NOT "X Y számára")
   - "in addition to X" → "X mellett/X-en kívül" (NOT "X számára")
   - "according to X" → "X szerint" (NOT "X-nek megfelelően" in most cases)
   - "similar to X" → "X-hez hasonló" (NOT "X számára hasonló")
"""
    
    def get_translation_examples(self) -> Optional[str]:
        """
        Returns examples of correct Hungarian translations.
        """
        return """
                
Examples of correct translations:
- "10 customers purchased" → "10 ügyfél vásárolt" 
- "Alternatives to [brokerName]" → "Alternatívák [brokerName] helyett"
- "across [dataPoints]+ criteria" → "[dataPoints]+ kritérium mentén"
- "Comparison to market average" → "Összehasonlítás a piaci átlaggal"
"""
    
    def get_evaluation_examples(self) -> Optional[str]:
        """
        Returns fewshot examples for Hungarian translation evaluation.
        """
        return """

Fewshot Examples:
| English | Correct Hungarian | Incorrect Hungarian | Note |
|---------|-------------------|---------------------|------|
| "10 customers purchased" | "10 ügyfél vásárolt" | "10 ügyfelek vásároltak" | Noun and verb both remain singular |
| "Several markets showed growth" | "Több piac mutatott növekedést" | "Több piacok mutattak növekedést" | Singular noun with singular verb |
| "across all parameters" | "minden paraméteren keresztül" | "minden paramétereken keresztül" | Singular noun with case ending |
| "Alternatives to [brokerName]" | "Alternatívák [brokerName] helyett" | "Alternatívák a [brokerName] számára" | "helyett" means "instead of", "számára" means "for" (different meaning) |
| "Comparison to market average" | "Összehasonlítás a piaci átlaggal" | "Összehasonlítás a piaci átlag számára" | Use instrumental case (-val/-vel), not "számára" |
"""


class TranslationRulesFactory:
    """
    Factory class for creating language-specific translation rule instances.
    """
    
    _rules_registry: Dict[str, TranslationRules] = {}
    _language_name_to_code: Dict[str, str] = {}
    
    @classmethod
    def register(cls, rules_class):
        """
        Register a translation rules implementation.
        
        Args:
            rules_class: A class that implements TranslationRules
        """
        instance = rules_class()
        language_code = instance.language_code.lower()
        language_name = instance.language_name.lower()
        
        # Store by code
        cls._rules_registry[language_code] = instance
        
        # Also map language name to code for lookup
        cls._language_name_to_code[language_name] = language_code
        
        return rules_class
    
    @classmethod
    def get_rules(cls, language_identifier: str) -> Optional[TranslationRules]:
        """
        Get translation rules for a specific language.
        Can be looked up by either language code (e.g., "hu") or name (e.g., "Hungarian").
        
        Args:
            language_identifier: The language code or name to get rules for
            
        Returns:
            Optional[TranslationRules]: The translation rules for the language or None if not found
        """
        language_identifier = language_identifier.lower()
        
        # Direct lookup by code
        if language_identifier in cls._rules_registry:
            return cls._rules_registry[language_identifier]
        
        # Lookup by language name
        if language_identifier in cls._language_name_to_code:
            code = cls._language_name_to_code[language_identifier]
            return cls._rules_registry[code]
        
        return None
    
    @classmethod
    def get_all_rules(cls) -> Dict[str, TranslationRules]:
        """
        Get all registered translation rules.
        
        Returns:
            Dict[str, TranslationRules]: Dictionary of language codes to rule instances
        """
        return cls._rules_registry


class GermanTranslationRules(TranslationRules):
    """
    German-specific translation rules implementation.
    """
    
    @property
    def language_code(self) -> str:
        return "de"
    
    @property
    def language_name(self) -> str:
        return "German"
    
    def get_rules(self) -> str:
        """
        Returns German-specific translation rules.
        """
        return """
German Translation Guidelines:

1. Noun Capitalization:
   - All nouns MUST be capitalized in German
   - Example: "the house" → "das Haus"
   - Example: "our company's services" → "die Dienstleistungen unserer Firma"

2. Compound Words:
   - German often combines multiple words into a single compound word
   - Example: "investment strategy" → "Anlagestrategie"
   - Example: "market analysis report" → "Marktanalysebericht"

3. Parameter Integration:
   - Parameters may require different article forms based on case (nominative, accusative, dative, genitive)
   - Example: "data from [brokerName]" → "Daten von [brokerName]" (dative case)
   - Example: "according to [sourceName]" → "laut [sourceName]" (dative case)

4. Sentence Structure:
   - German often places verbs in second position in main clauses and last position in subordinate clauses
   - Pay special attention to verb placement in complex sentences
"""
    
    def get_translation_examples(self) -> Optional[str]:
        """
        Returns examples of correct German translations.
        """
        return """
                
Examples of correct translations:
- "Market Report for 2023" → "Marktbericht für 2023"
- "Investment Strategy by [firmName]" → "Anlagestrategie von [firmName]"
- "10 key factors" → "10 wichtige Faktoren"
- "Comparison to industry standards" → "Vergleich mit Branchenstandards"
"""
    
    def get_evaluation_examples(self) -> Optional[str]:
        """
        Returns fewshot examples for German translation evaluation.
        """
        return """

Fewshot Examples:
| English | Correct German | Incorrect German | Note |
|---------|---------------|-----------------|------|
| "Financial Report" | "Finanzbericht" | "finanzbericht" | Nouns must be capitalized |
| "Data from [providerName]" | "Daten von [providerName]" | "Daten aus [providerName]" | "von" is the correct preposition for this context |
| "Investment Strategy" | "Anlagestrategie" | "Investment Strategie" | Use the German compound word rather than Anglicism |
| "market analysis tools" | "Marktanalysetools" | "Markt Analyse Tools" | Compound into a single word |
| "according to experts" | "laut Experten" | "nach Experten" | "laut" is more appropriate in this context |
"""


# Register all language rules
TranslationRulesFactory.register(HungarianTranslationRules)
TranslationRulesFactory.register(GermanTranslationRules)
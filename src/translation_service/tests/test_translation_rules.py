import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.translation_service.domain.model.translation_rules import (
    TranslationRules,
    HungarianTranslationRules,
    GermanTranslationRules,
    TranslationRulesFactory
)
from src.translation_service.domain.services.translation_system import TranslationSystem


class TestTranslationRules:
    def test_hungarian_rules_registration(self):
        """Test that Hungarian rules are registered with the factory"""
        rules = TranslationRulesFactory.get_rules("hu")
        assert rules is not None
        assert isinstance(rules, HungarianTranslationRules)
        assert rules.language_code == "hu"
        assert rules.language_name == "Hungarian"
    
    def test_get_all_rules(self):
        """Test getting all registered rules"""
        all_rules = TranslationRulesFactory.get_all_rules()
        assert "hu" in all_rules
        assert isinstance(all_rules["hu"], HungarianTranslationRules)
    
    def test_hungarian_rules_content(self):
        """Test that Hungarian rules content is correct"""
        rules = TranslationRulesFactory.get_rules("hu")
        
        # Check that rules contain key Hungarian translation guidelines
        assert "Quantity + Singular Noun Rule" in rules.get_rules()
        assert "Parameter Integration" in rules.get_rules()
        assert "\"To\" Preposition Translations" in rules.get_rules()
        assert "Common Patterns" in rules.get_rules()
        
        # Check that examples are included
        assert "10 ügyfél vásárolt" in rules.get_translation_examples()
        assert "Alternatívák [brokerName] helyett" in rules.get_translation_examples()
        
        # Check that evaluation examples are included
        eval_examples = rules.get_evaluation_examples()
        assert "Fewshot Examples" in eval_examples
        assert "Noun and verb both remain singular" in eval_examples
    
    def test_german_rules_registration(self):
        """Test that German rules are registered with the factory"""
        rules = TranslationRulesFactory.get_rules("de")
        assert rules is not None
        assert isinstance(rules, GermanTranslationRules)
        assert rules.language_code == "de"
        assert rules.language_name == "German"
    
    def test_german_rules_content(self):
        """Test that German rules content is correct"""
        rules = TranslationRulesFactory.get_rules("de")
        
        # Check that rules contain key German translation guidelines
        assert "Noun Capitalization" in rules.get_rules()
        assert "Compound Words" in rules.get_rules()
        assert "Parameter Integration" in rules.get_rules()
        assert "Sentence Structure" in rules.get_rules()
        
        # Check that examples are included
        assert "Marktbericht für 2023" in rules.get_translation_examples()
        assert "Anlagestrategie von [firmName]" in rules.get_translation_examples()
        
        # Check that evaluation examples are included
        eval_examples = rules.get_evaluation_examples()
        assert "Fewshot Examples" in eval_examples
        assert "Nouns must be capitalized" in eval_examples
    
    def test_translation_system_integration(self):
        """Test that TranslationSystem correctly uses the rules from factory"""
        translation_system = TranslationSystem()
        
        # Test Hungarian translation prompt
        hu_prompt = translation_system.get_translation_prompt("Hungarian")
        assert "Language-Specific Guidelines for Hungarian" in hu_prompt
        assert "Quantity + Singular Noun Rule" in hu_prompt
        assert "10 ügyfél vásárolt" in hu_prompt
        
        # Test Hungarian evaluation prompt
        original = "This is a test."
        translation = "Ez egy teszt."
        hu_eval_prompt = translation_system.create_evaluation_prompt(original, translation, "Hungarian")
        assert "IMPORTANT NOTE FOR HUNGARIAN TRANSLATIONS" in hu_eval_prompt
        assert "Quantity + Singular Noun Rule" in hu_eval_prompt
        assert "Fewshot Examples" in hu_eval_prompt
        
        # Test German translation prompt
        de_prompt = translation_system.get_translation_prompt("German")
        assert "Language-Specific Guidelines for German" in de_prompt
        assert "Noun Capitalization" in de_prompt
        assert "Marktbericht für 2023" in de_prompt
        
        # Test German evaluation prompt
        de_translation = "Das ist ein Test."
        de_eval_prompt = translation_system.create_evaluation_prompt(original, de_translation, "German")
        assert "IMPORTANT NOTE FOR GERMAN TRANSLATIONS" in de_eval_prompt
        assert "Noun Capitalization" in de_eval_prompt
        assert "Finanzbericht" in de_eval_prompt
        
        # Test with language that has no specific rules
        fr_prompt = translation_system.get_translation_prompt("French")
        assert "Language-Specific Guidelines for French" not in fr_prompt
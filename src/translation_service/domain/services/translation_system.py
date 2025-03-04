class TranslationSystem:
    def __init__(self):
        # Store language-specific rules that can be reused in both translation and evaluation
        self.language_rules = {
            "hungarian": self._get_hungarian_rules()
        }
    
    def _get_hungarian_rules(self):
        """
        Store Hungarian-specific translation rules.
        These rules are used both in translation prompts and evaluation prompts.
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
    
    def get_translation_prompt(self, language):
        """
        Creates a system prompt for translation.
        
        Args:
            language: The target language for translation
            
        Returns:
            A formatted system prompt string for LLM translation
        """
        # Base translation prompt
        prompt = (
            f"You are a professional translator. Translate the following "
            f"markdown content into {language}. Follow these rules strictly:\n"
            f"1. Maintain all original structure, formatting, and markdown syntax\n"
            f"2. DO NOT translate any text inside square brackets (e.g. [brokerName])\n"
            f"3. Ensure the translation sounds natural in {language}\n"
            f"4. Keep all placeholders exactly as they appear in the original text\n"
        )
        
        # Add language-specific rules if available
        language_key = language.lower()
        if language_key in self.language_rules:
            prompt += f"\n## Language-Specific Guidelines for {language}\n"
            prompt += self.language_rules[language_key]
            
            # Add specific examples for this language
            if language_key == "hungarian":
                prompt += """
                
Examples of correct translations:
- "10 customers purchased" → "10 ügyfél vásárolt" 
- "Alternatives to [brokerName]" → "Alternatívák [brokerName] helyett"
- "across [dataPoints]+ criteria" → "[dataPoints]+ kritérium mentén"
- "Comparison to market average" → "Összehasonlítás a piaci átlaggal"
"""
        
        return prompt
    
    def create_evaluation_prompt(self, original_text, translation, target_language):
        """
        Creates a system prompt for evaluating translation quality.
        
        Args:
            original_text: The source text in English
            translation: The translated text to evaluate
            target_language: The language of the translation
            
        Returns:
            A formatted system prompt string for LLM translation evaluation
        """
        # Truncate texts if they exceed token limits
        max_text_length = 1000
        
        if len(original_text) > max_text_length:
            original_text = original_text[:max_text_length] + "... [truncated]"
            
        if len(translation) > max_text_length:
            translation = translation[:max_text_length] + "... [truncated]"
        
        # Base evaluation prompt (as per your original)
        prompt = f"""# System Prompt for Translation Quality Evaluation

You are a specialized evaluator for translations in a financial/investment context. Your task is to assess the translation of the provided English text to {target_language}, evaluating for accuracy, naturalness, and cultural appropriateness, and provide standardized scores in a structured JSON format.

## Original Text
```
{original_text}
```

## Translation to Evaluate
```
{translation}
```

## Target Language
{target_language}

## Key Evaluation Criteria

1. **Grammatical Accuracy**
  - Ensure proper use of grammatical features specific to {target_language} (cases, gender, tense, etc.)
  - Check that all syntactic structures are correctly applied according to {target_language} rules
  - Pay special attention to how parameters and variables (marked with brackets like [countryName]) are integrated grammatically

2. **Number and Date Formatting**
  - Verify that numbers, currencies, dates, and other formatted elements follow {target_language} conventions
  - Check correct use of decimal and thousand separators according to local standards

3. **Terminology**
  - Identify inappropriately borrowed English terms when {target_language} equivalents exist
  - Financial terms should use standard {target_language} terminology when established
  - Check for industry-specific terms that may have standardized translations

4. **Word Order and Syntax**
  - Evaluate if the translation follows natural {target_language} syntax rather than mirroring English structure
  - Check if modifiers, adjectives, and other elements are placed correctly according to {target_language} norms

5. **Stylistic Appropriateness**
  - Assess if the translation uses unnecessarily verbose or overly literal constructions
  - Check if idiomatic expressions are appropriately adapted to {target_language}
  - Evaluate whether the formality level is appropriate for a financial/investment context

6. **Consistency**
  - Ensure product features, functions, and key terms are consistently translated
  - Check that recurring phrases maintain consistent translations throughout

7. **Parameter Handling**
  - Verify that dynamic parameters (marked with brackets like [countryName], [brokerName], etc.) are properly integrated with appropriate grammatical adaptations required by {target_language}
  - Check if numeric parameters need grammatical agreement (e.g., pluralization rules)

## Scoring System

For each metric below, you must assign a score from 1-5 based on EXACTLY these definitions:

### Accuracy (How accurately the translation conveys the meaning of the source text)
- Score 1: Complete mistranslation that changes the meaning entirely
- Score 2: Major inaccuracies that significantly alter the meaning
- Score 3: Some inaccuracies that slightly alter the meaning
- Score 4: Minor inaccuracies that don't significantly impact meaning
- Score 5: Perfect accuracy with all meaning correctly preserved

### Fluency (How naturally and smoothly the translation reads in {target_language})
- Score 1: Incomprehensible, not recognizable as {target_language}
- Score 2: Difficult to understand, sounds like machine translation
- Score 3: Understandable but with awkward phrasing
- Score 4: Mostly natural with minor awkwardness
- Score 5: Reads like it was originally written in {target_language}

### Adequacy (Whether all information is preserved without additions or omissions)
- Score 1: Most information missing or added incorrectly
- Score 2: Significant information missing or added unnecessarily
- Score 3: Some information missing or added unnecessarily
- Score 4: Minor details missing or added
- Score 5: All information perfectly preserved

### Consistency (Whether terminology and style are consistent throughout)
- Score 1: Completely inconsistent terminology and style
- Score 2: Major inconsistencies in key terms
- Score 3: Some noticeable inconsistencies
- Score 4: Few minor inconsistencies
- Score 5: Perfect consistency throughout

### Contextual_Appropriateness (Whether the translation is appropriate for the context and target audience)
- Score 1: Completely inappropriate for financial/investment context
- Score 2: Major issues with appropriateness
- Score 3: Some elements inappropriate for context
- Score 4: Minor issues with appropriateness
- Score 5: Perfectly appropriate for financial/investment context

### Terminology_Accuracy (Whether domain-specific terms are correctly translated)
- Score 1: Most financial terms incorrectly translated
- Score 2: Several major financial terms mistranslated
- Score 3: Some financial terms incorrectly translated
- Score 4: Minor issues with specialized terminology
- Score 5: All financial/investment terms correctly translated

### Readability (How clear and easy to understand the text is)
- Score 1: Incomprehensible
- Score 2: Very difficult to understand
- Score 3: Requires effort to understand
- Score 4: Easy to understand with minor clarity issues
- Score 5: Perfectly clear and easy to understand

### Format_Preservation (Whether the original formatting and layout are maintained)
- Score 1: Format completely altered
- Score 2: Major formatting issues
- Score 3: Some formatting inconsistencies
- Score 4: Minor formatting differences
- Score 5: Perfect preservation of format

### Error_Rate (Absence of grammatical or typographical errors)
- Score 1: Numerous serious errors throughout
- Score 2: Several major errors
- Score 3: Some noticeable errors
- Score 4: Few minor errors
- Score 5: No errors detected

## Response Format

You must return your evaluation ONLY as a valid JSON object. Do not include any text before or after the JSON. The response must be parseable by a JSON parser. 

Your response must follow this exact structure:

```json
{{
  "Accuracy": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Fluency": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Adequacy": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Consistency": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Contextual_Appropriateness": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Terminology_Accuracy": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Readability": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Format_Preservation": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }},
  "Error_Rate": {{
    "score": [integer between 1-5],
    "explanation": "Detailed explanation of the score."
  }}
}}
```

IMPORTANT: 
1. The response must be VALID JSON only. Do not include any explanatory text, markdown formatting, or any other content outside of the JSON object.
2. The JSON must be properly formatted with all quotation marks, commas, and brackets in the correct places.
3. Scores must be integers between 1-5, not strings or arrays.
4. Always use the exact score definitions provided above to determine the appropriate score.
5. For each metric, reference the specific definition for that score level in your explanation.

## Final Notes for Accurate Evaluation

- Always consider {target_language} linguistic norms over literal translations
- Pay special attention to cases where parameters ([countryName], [brokerName], etc.) would require grammatical adaptations specific to {target_language}
- Consider the financial/investment context of the translations
- Focus on both technical accuracy and natural-sounding {target_language}
- Be aware of regional variations within {target_language} if applicable
"""

        # Add language-specific rules if available
        target_language_key = target_language.lower()
        if target_language_key in self.language_rules:
            prompt += f"\n\n## IMPORTANT NOTE FOR {target_language.upper()} TRANSLATIONS\n"
            prompt += self.language_rules[target_language_key]
            
            # Add specific fewshot examples for this language
            if target_language_key == "hungarian":
                prompt += """

Fewshot Examples:
| English | Correct Hungarian | Incorrect Hungarian | Note |
|---------|-------------------|---------------------|------|
| "10 customers purchased" | "10 ügyfél vásárolt" | "10 ügyfelek vásároltak" | Noun and verb both remain singular |
| "Several markets showed growth" | "Több piac mutatott növekedést" | "Több piacok mutattak növekedést" | Singular noun with singular verb |
| "across all parameters" | "minden paraméteren keresztül" | "minden paramétereken keresztül" | Singular noun with case ending |
| "Alternatives to [brokerName]" | "Alternatívák [brokerName] helyett" | "Alternatívák a [brokerName] számára" | "helyett" means "instead of", "számára" means "for" (different meaning) |
| "Comparison to market average" | "Összehasonlítás a piaci átlaggal" | "Összehasonlítás a piaci átlag számára" | Use instrumental case (-val/-vel), not "számára" |
"""
        
        return prompt
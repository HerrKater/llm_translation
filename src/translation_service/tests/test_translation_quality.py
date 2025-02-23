import csv
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from application.translation_service import TranslationService
from infrastructure.translator import OpenAITranslator
from dataclasses import dataclass

@dataclass
class TranslationRequest:
    source_content: str
    target_languages: list[str]
from infrastructure.config import Settings
from infrastructure.web_crawler import HttpWebCrawler
from infrastructure.markdown_content_processor import MarkdownContentProcessor
import openai
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List
import json

load_dotenv()

class TranslationEvaluator:
    def __init__(self):
        settings = Settings()
        self.translator = OpenAITranslator(settings)
        self.openai_client = openai.OpenAI(
            base_url=os.getenv("OPENAI_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def evaluate_translation(self, english_text: str, reference_translation: str, new_translation: str) -> Dict:
        """Use LLM to evaluate the translation quality."""
        prompt = f"""You are a Hungarian language expert. Please evaluate the following translation from English to Hungarian:

Original English text: {english_text}
Reference translation: {reference_translation}
New translation: {new_translation}

Please analyze the translations and provide a JSON response with the following structure:
{{
    "accuracy_score": <score from 0-10>,
    "fluency_score": <score from 0-10>,
    "matches_reference": <true/false>,
    "comments": "<brief explanation of the evaluation>"
}}

Focus on semantic accuracy, fluency, and whether the new translation conveys the same meaning as the reference."""

        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_LANGUAGE_MODEL"),
            messages=[{"role": "system", "content": "You are a Hungarian language expert. Provide evaluation in the exact JSON format requested."},
                     {"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "accuracy_score": 0,
                "fluency_score": 0,
                "matches_reference": False,
                "comments": "Error parsing LLM response"
            }

    async def run_evaluation(self, csv_path: str) -> List[Dict]:
        """Run evaluation on all translations in the CSV file."""
        results = []
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            english_text = row['english']
            reference_translation = row['translated_value']
            
            # Get new translation
            request = TranslationRequest(source_content=english_text, target_languages=['hu'])
            translation = await self.translator.translate(request)
            new_translation = translation.translations['hu']
            
            # Evaluate translation
            evaluation = await self.evaluate_translation(
                english_text, 
                reference_translation, 
                new_translation
            )
            
            results.append({
                'english_text': english_text,
                'reference_translation': reference_translation,
                'new_translation': new_translation,
                'evaluation': evaluation
            })
            
        return results

async def main():
    evaluator = TranslationEvaluator()
    csv_path = Path(__file__).parent / 'translated_output.csv'
    
    print("Starting translation evaluation...")
    results = await evaluator.run_evaluation(str(csv_path))
    
    # Calculate average scores
    accuracy_scores = [r['evaluation']['accuracy_score'] for r in results]
    fluency_scores = [r['evaluation']['fluency_score'] for r in results]
    match_count = sum(1 for r in results if r['evaluation']['matches_reference'])
    
    print("\nEvaluation Summary:")
    print(f"Average Accuracy Score: {sum(accuracy_scores)/len(accuracy_scores):.2f}")
    print(f"Average Fluency Score: {sum(fluency_scores)/len(fluency_scores):.2f}")
    print(f"Reference Match Rate: {match_count/len(results)*100:.2f}%")
    
    # Save detailed results
    output_path = Path(__file__).parent / 'translation_evaluation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

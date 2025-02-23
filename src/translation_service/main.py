from io import StringIO
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from domain.model.settings import get_settings
from domain.model.translation_request import TranslationRequest
from interfaces.evaluation_models import BatchEvaluationRequest, BatchEvaluationResponse, TranslationEvaluationResult, LLMEvaluation
from domain.services.llm_translation_evaluator_service import LlmTranslationEvaluatorService
from infrastructure.http_web_crawler import HttpWebCrawler
from infrastructure.markdown_content_processor import MarkdownContentProcessor
from domain.services.llm_translator_service import LlmTranslatorService
from application.translation_orchestrator import TranslationOrchestrator
from interfaces.api_models import TranslationRequestDTO, RawTextTranslationRequestDTO, TranslationResponseDTO

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize settings and services
settings = get_settings()
translator = LlmTranslatorService(settings)
evaluator = LlmTranslationEvaluatorService(settings)
crawler = HttpWebCrawler()
processor = MarkdownContentProcessor()
translation_service = TranslationOrchestrator(crawler, processor, translator)

@app.post("/translate", response_model=TranslationResponseDTO)
async def translate_url(request: TranslationRequestDTO):
    try:
        # Perform translation
        translation = await translation_service.translate_webpage(
            str(request.url),
            request.target_languages
        )
        
        # Convert domain model to DTO
        return TranslationResponseDTO(
            original_text=translation.original_content,
            translations=translation.translations
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate/raw", response_model=TranslationResponseDTO)
async def translate_raw_text(request: RawTextTranslationRequestDTO):
    try:
        # Create a translation request object
        translation_request = TranslationRequest(
            source_content=request.text,
            target_languages=request.target_languages
        )
        
        # Translate using the request object
        translation = await translator.translate(translation_request)
        
        return TranslationResponseDTO(
            original_text=request.text,
            translations=translation.translations
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-translations")
async def evaluate_translations(file: UploadFile):
    try:
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode()))
        
        results = []
        for _, row in df.iterrows():
            # Get source and reference texts
            source_text = row['english']
            reference_translation = row['translated_value']
            
            # Get new translation
            request = TranslationRequest(source_content=source_text, target_languages=['hu'])
            translation = await translator.translate(request)
            new_translation = translation.translations['hu']
            
            # Evaluate translation
            llm_eval = await evaluator.evaluate_translation(
                source_text,
                reference_translation,
                new_translation
            )

            results.append(TranslationEvaluationResult(
                source_text=source_text,
                reference_translation=reference_translation,
                new_translation=new_translation,
                llm_evaluation=LLMEvaluation(
                    accuracy_score=llm_eval.accuracy_score,
                    fluency_score=llm_eval.fluency_score,
                    matches_reference=llm_eval.matches_reference,
                    comments=llm_eval.comments
                )
            ))
        
        # Calculate summary statistics
        summary = {
            'avg_accuracy': sum(r.llm_evaluation.accuracy_score for r in results) / len(results),
            'avg_fluency': sum(r.llm_evaluation.fluency_score for r in results) / len(results)
        }
        
        return BatchEvaluationResponse(results=results, summary=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    response = FileResponse("static/index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

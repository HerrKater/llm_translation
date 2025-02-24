from io import StringIO
import asyncio
import pandas as pd
from typing import Dict, List
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from domain.model.settings import get_settings
from domain.model.language_settings import language_settings
from domain.model.language_models import ModelName, LanguageModels
from domain.model.translation_request import TranslationRequest
from domain.services.llm_translation_evaluator_service import LlmTranslationEvaluatorService
from infrastructure.http_web_crawler import HttpWebCrawler
from infrastructure.markdown_content_processor import MarkdownContentProcessor
from domain.services.llm_translator_service import LlmTranslatorService
from application.translation_orchestrator import TranslationOrchestrator
from application.translation_evaluation_orchestrator import TranslationEvaluationOrchestrator
from interfaces.api_models import (TranslationRequestDTO, RawTextTranslationRequestDTO,
    TranslationResponseDTO, CostInfoDTO, ModelConfigDTO)

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
evaluation_service = TranslationEvaluationOrchestrator(translator, evaluator)

@app.post("/translate", response_model=TranslationResponseDTO)
async def translate_url(request: TranslationRequestDTO):
    try:
        # Perform translation
        translation, cost_info = await translation_service.translate_webpage(
            str(request.url),
            request.target_languages
        )
        
        # Convert domain model to DTO
        return TranslationResponseDTO(
            original_text=translation.original_content,
            translations=translation.translations,
            cost_info=CostInfoDTO(
                total_cost=cost_info['total_cost'],
                input_cost=cost_info['input_cost'],
                output_cost=cost_info['output_cost'],
                input_tokens=cost_info['input_tokens'],
                output_tokens=cost_info['output_tokens'],
                model=cost_info['model']
            )
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
        translation, cost_info = await translator.translate(translation_request)
        
        return TranslationResponseDTO(
            original_text=request.text,
            translations=translation.translations,
            cost_info=CostInfoDTO(
                total_cost=cost_info['input_cost']+cost_info['output_cost'],
                input_cost=cost_info['input_cost'],
                output_cost=cost_info['output_cost'],
                input_tokens=cost_info['input_tokens'],
                output_tokens=cost_info['output_tokens'],
                model=cost_info['model']
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-translations")
async def evaluate_translations(
    file: UploadFile, 
    target_language: str = Form(...),
    translation_model: str = Form(...),
    evaluation_model: str = Form(...)
):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Please upload a CSV file")

        # Read file content
        content = await file.read()
        
        try:
            response = await evaluation_service.evaluate_translations(
                content,
                target_language,
                translation_model,
                evaluation_model
            )
            return response
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models", response_model=Dict[str, List[ModelConfigDTO]])
def get_models():
    """Get available language models and their configurations"""
    models = []
    for model_config in LanguageModels.get_all_models():
        models.append(ModelConfigDTO(
            id=model_config.name.value,
            name=model_config.display_name,
            description=model_config.description,
            inputCost=model_config.input_cost_per_1k,
            outputCost=model_config.output_cost_per_1k,
            maxTokens=model_config.max_tokens
        ))
    return {"models": models}

@app.get("/")
async def read_root():
    response = FileResponse("static/index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

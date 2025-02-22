from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict

from infrastructure.config import get_settings
from infrastructure.web_crawler import HttpWebCrawler
from infrastructure.content_processor import MarkdownContentProcessor
from infrastructure.translator import OpenAITranslator
from application.translation_service import TranslationService
from interfaces.api_models import TranslationRequestDTO, TranslationResponseDTO

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
translator = OpenAITranslator(settings)
crawler = HttpWebCrawler()
processor = MarkdownContentProcessor()
translation_service = TranslationService(crawler, processor, translator)

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

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

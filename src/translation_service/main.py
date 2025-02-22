from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import openai
import httpx
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with custom configuration
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_URL"),
    default_headers={"api-version": os.getenv("OPENAI_API_VERSION")},
    http_client=httpx.Client(
        base_url=os.getenv("OPENAI_URL"),
        headers={"api-version": os.getenv("OPENAI_API_VERSION")}
    )
)

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

class TranslationRequest(BaseModel):
    url: str
    target_languages: List[str]

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:4000]  # Limit text length to manage API costs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

def translate_text(text: str, target_language: str) -> str:
    try:
        system_prompt = f"""You are a professional translator. Translate the following text into {target_language}.
        Maintain the original meaning and tone while ensuring the translation sounds natural in the target language."""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_LANGUAGE_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@app.post("/translate")
async def translate_url(request: TranslationRequest):
    # Extract text from URL
    text = extract_text_from_url(request.url)
    
    # Translate to each target language
    translations = {}
    for language in request.target_languages:
        translations[language] = translate_text(text, language)
    
    return {
        "original_text": text,
        "translations": translations
    }

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

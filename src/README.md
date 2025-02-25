# Translation Service

A service for evaluating translation quality using LLM-based translation and evaluation.

## Prerequisites

- Python 3.12+
- OpenAI API key

## Setup Instructions

### 1. Install Dependencies

```bash
# Install the requirements
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual OpenAI API key.

### 3. Running Translation Quality Tests

```bash
# Run the translation quality test
python tests/test_translation_quality.py
```

The test will:
1. Read English text samples from `tests/translated_output.csv`
2. Generate new translations using the LLM translator
3. Evaluate translation quality using the LLM evaluator
4. Save detailed results to `tests/translation_evaluation_results.json`

## Project Structure

```
translation_service/
├── domain/           # Core translation and evaluation logic
│   ├── model/       # Domain models and data structures
│   └── services/    # Translation and evaluation services
├── tests/           # Translation quality tests
```
├── main.py          # FastAPI application entry point
└── requirements.txt  # Project dependencies
```

## API Endpoints

The service provides the following main endpoints:

- `/`: Returns the main web interface
- `/translate`: Translates content from a URL
- `/translate/raw`: Translates raw text content
- `/api/evaluate-translations`: Evaluates translations from a CSV file
- `/api/models`: Returns available language models and their configurations

For detailed API documentation, visit the `/docs` endpoint after starting the server.



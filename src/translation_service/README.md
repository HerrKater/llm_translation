# Translation Service

A FastAPI-based service for handling translations with terminology awareness and language model integration.

## Prerequisites

- Python 3.9+
- Conda (Miniconda or Anaconda)
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create and Activate Conda Environment

```bash
# Create a new conda environment
conda create -n translation_service python=3.9

# Activate the environment
conda activate translation_service
```

### 3. Install Dependencies

```bash
# Navigate to the translation service directory
cd src/translation_service

# Install the requirements
pip install -r requirements.txt

```

### 4. Environment Configuration

Create a `.env` file in the `src/translation_service` directory with the following template:

```env
# OpenAI Configuration
OPENAI_URL=your_openai_url_here
OPENAI_API_KEY=your_api_key_here
```

Replace the placeholder values with your actual configuration.

### 5. Running the Application

```bash
# Make sure you're in the translation_service directory
cd src/translation_service

# Start the application with hot reload
uvicorn main:app --reload

```

The application will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative API Documentation: `http://localhost:8000/redoc`

### 6. Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. tests/

# Run specific test file
pytest tests/test_specific_file.py
```

### 7. Code Quality Tools

```bash
# Run type checking
mypy .

# Run code linting
ruff check .
```

## Project Structure

```
translation_service/
├── application/       # Application layer with use cases
├── domain/           # Domain layer with core business logic
├── infrastructure/   # Infrastructure layer (external services, databases)
├── interfaces/       # Interface adapters
├── static/          # Static files
├── tests/           # Test files
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



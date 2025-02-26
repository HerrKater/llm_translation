# Translation Service

A service for evaluating translation quality using LLM-based translation and evaluation, built following Clean Architecture (also known as Onion Architecture) principles to ensure separation of concerns, maintainability, and testability.

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
OPENAI_URL=your_openai_compatible_url_here
OPENAI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual OpenAI API key and `your_openai_compatible_url_here` with the appropriate endpoint URL.

Note: This code was tested against a LiteLLM server providing an OpenAI-compatible interface, which is why Claude models appear in the configuration. If you're using different model names, you'll need to modify the values in `domain/models/language_models.py` where these are hard-coded.

### 3. Starting the Application

```bash
# Start the FastAPI application
uvicorn translation_service.main:app
```

### 4. Running Translation Quality Tests

```bash
# Run the translation quality test
python tests/test_translation_quality.py
```

The test will:
1. Read English text samples from `tests/translated_output.csv`
2. Generate new translations using the LLM translator
3. Evaluate translation quality using the LLM evaluator
4. Save detailed results to `tests/translation_evaluation_results.json`

## API Endpoints

The service provides the following main endpoints:

- `/`: Returns the main web interface
- `/translate`: Translates content from a URL
- `/translate/raw`: Translates raw text content
- `/api/evaluate-translations`: Evaluates translations from a CSV file
- `/api/models`: Returns available language models and their configurations

For detailed API documentation, visit the `/docs` endpoint after starting the server.

## Project Architecture

The project follows a layered architecture pattern where dependencies flow inward. Each layer has a specific responsibility and can only depend on layers that are more central to it.

```
translation_service/
├── domain/           # Core business logic and entities
│   ├── model/        # Domain models and data structures
│   └── services/     # Translation and evaluation services
├── application/      # Use cases and application services
├── infrastructure/   # External services implementation
├── interfaces/       # API endpoints and controllers
├── static/          # Static assets
├── main.py          # FastAPI application entry point 
├── tests/           # Test suite
└── requirements.txt  # Project dependencies
```

### Architectural Layers

#### 1. Domain Layer (`domain/`)
- The core of the application containing business logic and rules
- Has no dependencies on other layers
- Defines interfaces (abstract classes) that outer layers must implement
- Contains:
  - Entity models
  - Value objects
  - Domain services
  - Repository interfaces

#### 2. Application Layer (`application/`)
- Contains application-specific business rules
- Orchestrates the flow of data and implements use cases
- Depends only on the domain layer
- Contains:
  - Use case implementations
  - Service orchestrators
  - DTOs (Data Transfer Objects)

#### 3. Infrastructure Layer (`infrastructure/`)
- Implements interfaces defined in the domain layer
- Contains concrete implementations of:
  - External service integrations
  - Database repositories
  - Third-party APIs
  - Technical services

#### 4. Interfaces Layer (`interfaces/`)
- The outermost layer
- Contains:
  - API endpoints
  - Controllers
  - Request/Response models
  - Route definitions

### Dependency Inversion

The architecture strictly follows the Dependency Inversion Principle:
- High-level modules (domain, application) don't depend on low-level modules (infrastructure)
- Both depend on abstractions (interfaces)
- Abstractions don't depend on details; details depend on abstractions

For example:
- The domain layer defines repository interfaces
- The infrastructure layer implements these interfaces
- The application layer uses the interfaces, not the concrete implementations

This approach allows for:
- Easy testing through dependency injection
- Swapping implementations without changing business logic
- Better separation of concerns
- Increased maintainability
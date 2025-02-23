# Unit Tests

This directory contains unit tests for the domain services using pytest and pytest-asyncio.

## Setup

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=domain
```

## Test Structure

- `conftest.py`: Common test fixtures and configuration
- `test_llm_translator_service.py`: Tests for LlmTranslatorService
- `test_llm_translation_evaluator_service.py`: Tests for LlmTranslationEvaluatorService
- `test_web_crawler_repository.py`: Tests for WebCrawlerRepository
- `test_content_processor.py`: Tests for ContentProcessor

## Test Design

Each test file follows these principles:
1. Uses pytest fixtures for common setup
2. Mocks external dependencies (LLM client, HTTP client)
3. Tests both success and error cases
4. Verifies correct interface implementation
5. Uses type hints and assertions

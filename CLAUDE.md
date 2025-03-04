# BrokerChooser2 Translation Service

## Commands
- Run server: `python src/translation_service/main.py`
- Run tests: `pytest src/translation_service/tests/`
- Run specific test: `pytest src/translation_service/tests/test_translation_quality.py`
- Type checking: `mypy src/translation_service/`
- Linting: `ruff src/translation_service/`
- Install dependencies: `pip install -r src/translation_service/requirements.txt`
- Install test dependencies: `pip install -r src/translation_service/tests/requirements_test.txt`

## Code Style Guidelines
- **Imports**: Group imports by standard lib, third-party, and internal packages
- **Typing**: Use type hints for all function parameters and return values
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except blocks with specific exceptions
- **Architecture**: Follow domain-driven design with clean separation of concerns
- **Docstrings**: Use triple quotes for all public functions and classes
- **Testing**: Write async tests with pytest-asyncio for async functions
- **Models**: Use dataclasses or Pydantic models for data structures
# LLM-Runner Developer Guidelines

## Build & Test Commands
- `make test` - Run all tests, doctest, mypy, and codespell
- `make pytest` - Run all pytest tests
- `poetry run pytest tests/test_file.py::TestClass::test_function` - Run a single test
- `make mypy` - Run type checking
- `tox -e lint` - Run linters (black, ruff)
- `tox -e lint-fix` - Auto-fix linting issues
- `tox -e codespell` - Check spelling

## Code Style
- **Imports**: Standard lib first, third-party second, local imports last
- **Formatting**: Black (120 chars), 4-space indentation
- **Linting**: Ruff for style (pycodestyle, pyflakes, bugbear, isort)
- **Types**: Use type hints everywhere, import types from typing module
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Documentation**: Detailed docstrings with examples and type info
- **Error Handling**: Use logging, specific exceptions with descriptive messages
- **Testing**: Mark LLM tests with @pytest.mark.llm
- **Models**: Use Pydantic for data validation

## Development Setup
- Poetry for dependency management
- Python 3.11+
- Virtual environment recommended
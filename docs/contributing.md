# Contributing to LLM Matrix

We welcome contributions to LLM Matrix! This document provides guidelines and instructions for contributing.

## Development Environment

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/monarch-initiative/llm-matrix.git
   cd llm-matrix
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

3. Activate the virtual environment:

   ```bash
   poetry shell
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatter with 120 character line length
- **Ruff**: Linter with various rules (flake8, isort, etc.)
- **MyPy**: Static type checking

To check code quality:

```bash
# Run type checking
make mypy

# Run linters
tox -e lint

# Auto-fix linting issues where possible
tox -e lint-fix

# Check spelling
tox -e codespell
```

### Running Tests

```bash
# Run all tests, doctest, mypy, and codespell
make test

# Run only pytest tests
make pytest

# Run a specific test
poetry run pytest tests/test_file.py::TestClass::test_function
```

## Making Changes

1. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our code style guidelines.

3. Add tests for new functionality.

4. Ensure all tests pass:

   ```bash
   make test
   ```

5. Update documentation as needed.

## Submitting Changes

1. Push your changes to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub.

3. Ensure the PR description clearly describes the problem and solution.

## Adding New Metrics

To add a new evaluation metric:

1. Create a new class in `src/llm_matrix/metrics.py` that inherits from `Metric`:

   ```python
   class MyNewMetric(Metric):
       def evaluate(self, case: TestCase, response: LLMResponse) -> EvalResult:
           # Implement your evaluation logic
           score = calculate_score(case.ideal, response.text)
           
           return EvalResult(
               score=score,
               explanation="Reason for this score"
           )
   ```

2. Register your metric:

   ```python
   register_metric("my_new_metric", MyNewMetric())
   ```

3. Add tests for your metric in `tests/test_metrics.py`.

4. Update documentation in `docs/metrics/index.md`.

## Creating Plugins

To create a new plugin:

1. Create a new file in `src/llm_matrix/plugins/` (e.g., `my_plugin.py`).

2. Implement the plugin interface:

   ```python
   from llm_matrix.plugins.plugin import Plugin

   class MyPlugin(Plugin):
       def name(self) -> str:
           return "my_plugin"
       
       # Implement required methods
   ```

3. Register your plugin in `src/llm_matrix/plugins/__init__.py`.

4. Add tests for your plugin in `tests/test_plugins/`.

5. Update documentation as needed.

## Documentation

We use MkDocs with the Material theme for documentation:

1. Update documentation as needed in the `docs/` directory.

2. Preview documentation locally:

   ```bash
   mkdocs serve
   ```

3. Ensure all links and references are correct.

## Release Process

1. Update version number in `pyproject.toml`.
2. Update CHANGELOG.md with changes in the release.
3. Create a tag with the new version number.
4. A GitHub Action will automatically build and publish to PyPI.

## Questions?

If you have any questions, please open an issue on GitHub or reach out to the maintainers.
# LLM Matrix: Batch Run and Evaluate LLM Cases

LLM Matrix is a tool for running, evaluating, and comparing different language models across a matrix of hyperparameters. It allows systematic testing of models for accuracy, consistency, and performance on specific tasks.

## Features

- Define test suites with multiple cases in YAML
- Run test suites against different models with various hyperparameters
- Cache results to avoid redundant API calls
- Generate detailed reports and statistics on model performance  
- Support for various evaluation metrics
- Plugin system for extending functionality

## Installation

### From PyPI (Recommended)

```bash
pip install llm-matrix
```

### With Optional Dependencies

```bash
# For Excel report support
pip install "llm-matrix[excel]"

# For MLflow integration
pip install "llm-matrix[mlflow]"

# For LinkML mapping support
pip install "llm-matrix[map]"

# Install all extras
pip install "llm-matrix[excel,mlflow,map]"
```

## Quick Start

### 1. Create a Test Suite YAML

```yaml
name: simple-test
template: binary_with_explanation
templates:
  binary_with_explanation:
    system: Is the provided statement true? Return YES, NO, or OTHER, followed by an explanation.
      The explanation can be of any form and length but your response must start with YES, NO, or OTHER.
    prompt: "{input}"
    metrics:
      - qa_with_explanation
matrix:
  hyperparameters:
    model: [gpt-4o, gpt-3.5-turbo]
    temperature: [0.0, 2.0]
cases:
  - input: decyl palmitate is classified as a wax ester
    ideal: YES. It is formed by the esterification of decyl alcohol and palmitic acid.
    tags: [chemistry]
  - input: "1 + 1 = 2"
    ideal: "YES"
    tags: [arithmetic]
```

### 2. Run the Test Suite

```bash
llm-matrix run my-test-suite.yaml
```

### 3. View Results

Results are saved in the `-output` directory by default:

```
my-test-suite-output/
├── by_model.csv             # Performance summary by model
├── by_model_ideal.csv       # Performance by model and ideal answer
├── grouped_by_input.tsv     # Detailed view of each test case
├── grouped_by_input.xlsx    # Excel version of the above
├── results.csv              # Raw results
├── results.html             # HTML view of raw results
├── summary.csv              # Statistical summary
└── summary.html             # HTML view of summary
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/monarch-initiative/llm-runner.git
cd llm-runner

# Install with development dependencies
poetry install

# Activate the virtual environment
poetry shell
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

### Code Quality

```bash
# Type checking
make mypy

# Run linters (black, ruff)
tox -e lint

# Auto-fix linting issues
tox -e lint-fix

# Check spelling
tox -e codespell
```

## Documentation

Full documentation is available at [https://monarch-initiative.github.io/llm-runner/](https://monarch-initiative.github.io/llm-runner/)

## License

MIT
# LLM Matrix

LLM Matrix is a tool for running, evaluating, and comparing different language models across a matrix of hyperparameters.

## Overview

LLM Matrix enables you to:

- Define test suites with multiple cases in YAML
- Run test cases across different models and parameters
- Evaluate model responses using specialized metrics
- Generate comprehensive reports to analyze performance
- Compare results across models and parameters

## Key Concepts

### Test Suites

A test suite is a YAML file that defines:

- Test cases (inputs and expected outputs)
- Templates for system and user prompts
- Models to test
- Hyperparameters to vary
- Metrics for evaluation

### Matrix Execution

LLM Matrix runs each test case against a matrix of parameters, such as:

- Different LLM models (e.g., GPT-4, Claude)
- Various temperature settings
- Different prompt templates

### Metrics

Custom metrics evaluate model outputs by comparing them to ideal answers:

- QA metrics for question-answering tasks
- Binary classification metrics (YES/NO questions)
- List matching metrics for enumeration tasks

### Result Analysis

After running a test suite, you can analyze:

- Model performance by score
- Statistical summaries
- Per-case breakdowns
- Comparisons across models and parameters

## Installation

```bash
pip install llm-matrix
```

For optional features:

```bash
# Excel report support
pip install "llm-matrix[excel]"

# MLflow integration
pip install "llm-matrix[mlflow]"

# LinkML mapping support
pip install "llm-matrix[map]"
```

## Quick Links

- [Tutorial](tutorial/index.md) - Get started with LLM Matrix
- [Configuration](configuration/index.md) - Learn how to configure test suites
- [Metrics](metrics/index.md) - Available metrics for evaluation
- [CLI](cli.md) - Command-line interface reference
- [API Reference](api/index.md) - Python API documentation
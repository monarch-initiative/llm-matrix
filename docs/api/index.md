# API Reference

This section provides detailed documentation of the LLM Matrix Python API.

## Core Modules

### LLMRunner

The main class for running evaluations.

```python
from llm_matrix import LLMRunner

runner = LLMRunner(store_path="results.db")
results = runner.run(suite)
```

::: llm_matrix.LLMRunner

### Schema

Data models for test cases, templates, responses, and results.

::: llm_matrix.schema

### Metrics

Evaluation metrics for comparing model outputs to expected answers.

::: llm_matrix.metrics

### Store

Cache for storing results and avoiding redundant API calls.

::: llm_matrix.store

## Using the API

### Basic Example

```python
from llm_matrix import LLMRunner
from llm_matrix.schema import load_suite

# Load a test suite from YAML
suite = load_suite("my-suite.yaml")

# Create a runner
runner = LLMRunner(store_path="results.db")

# Run the suite
results = runner.run(suite)

# Process results
for result in results:
    print(f"Case: {result.case.input}")
    print(f"Score: {result.score}")
    print(f"Response: {result.response.text}")
```

### Custom Configuration

```python
from llm_matrix import LLMRunner
from llm_matrix.runner import LLMRunnerConfig

# Create custom configuration
config = LLMRunnerConfig(
    concurrency=5,
    retries=3,
    timeout=30
)

# Initialize runner with configuration
runner = LLMRunner(
    store_path="results.db",
    config=config
)
```

### Working with Results

```python
from llm_matrix.schema import results_to_dataframe

# Convert results to pandas DataFrame
df = results_to_dataframe(results)

# Calculate statistics
print(df.describe())

# Group by model
model_performance = df.groupby("model").agg({
    "score": ["mean", "std", "count"]
})
```

### Creating Test Suites Programmatically

```python
from llm_matrix.schema import TestSuite, TestCase, Template

# Create templates
templates = {
    "qa_template": Template(
        system="Answer the following question accurately.",
        prompt="{input}",
        metrics=["qa_simple"]
    )
}

# Create test cases
cases = [
    TestCase(
        input="What is the capital of France?",
        ideal="Paris",
        tags=["geography"]
    ),
    TestCase(
        input="What is 2+2?",
        ideal="4",
        tags=["math"]
    )
]

# Create test suite
suite = TestSuite(
    name="programmatic-suite",
    template="qa_template",
    templates=templates,
    cases=cases,
    matrix={
        "hyperparameters": {
            "model": ["gpt-3.5-turbo", "gpt-4o"],
            "temperature": [0.0]
        }
    }
)

# Run the suite
runner = LLMRunner(store_path="results.db")
results = runner.run(suite)
```
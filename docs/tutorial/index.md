# Getting Started with LLM Matrix

This tutorial walks you through the basic usage of LLM Matrix, from installation to running your first evaluation.

## Installation

Install LLM Matrix using pip:

```bash
pip install llm-matrix
```

## Creating Your First Test Suite

Create a file named `first-test.yaml` with the following content:

```yaml
name: my-first-test
template: simple_qa
templates:
  simple_qa:
    system: Answer the following question accurately and concisely.
    prompt: "{input}"
    metrics:
      - qa_simple
matrix:
  hyperparameters:
    model: [gpt-3.5-turbo]
    temperature: [0.0]
cases:
  - input: What is the capital of France?
    ideal: Paris
    tags: [geography]
  - input: What is 2+2?
    ideal: "4"
    tags: [math]
```

### Understanding the YAML Structure

- `name`: Identifier for your test suite
- `template`: Default template to use
- `templates`: Define different prompt templates
  - `system`: System instructions to the model
  - `prompt`: Template for user prompt (with variables in curly braces)
  - `metrics`: Evaluation metrics to apply
- `matrix.hyperparameters`: Parameters to vary in the test
- `cases`: Individual test cases
  - `input`: Query to send to the model
  - `ideal`: Expected response (used for evaluation)
  - `tags`: Optional categorization

## Running the Test Suite

Execute your test suite with:

```bash
llm-matrix run first-test.yaml
```

This will:
1. Create a database file to cache results
2. Run each test case against the specified model(s)
3. Generate evaluation reports

## Viewing Results

After running the test suite, you'll find a `first-test-output` directory with:

- `results.csv`: Raw results for all runs
- `summary.csv`: Statistical summary of model performance
- `by_model.csv`: Performance breakdown by model
- `grouped_by_input.tsv`: Detailed breakdown by test case

## Next Steps

- [Configuring Test Suites](../configuration/index.md): Learn about advanced configuration options
- [Understanding Metrics](../metrics/index.md): Explore different evaluation metrics
- [CLI Reference](../cli.md): Discover all command-line options
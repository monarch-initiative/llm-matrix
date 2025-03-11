# Configuration Guide

This guide covers how to configure LLM Matrix test suites and runners.

## Test Suite Configuration

Test suites are defined in YAML files with the following structure:

```yaml
name: suite-name
template: default-template-name
templates:
  template-name:
    system: System prompt text
    prompt: User prompt template with {variables}
    metrics:
      - metric_name1
      - metric_name2
matrix:
  hyperparameters:
    model: [model1, model2]
    temperature: [0.0, 0.7]
    # Other parameters as needed
cases:
  - input: Input text for the first case
    ideal: Expected output text
    tags: [tag1, tag2]
  - input: Input text for the second case
    ideal: Expected output text
    tags: [tag3]
    # Case-specific parameters to override defaults
    template: special-template 
```

### Core Components

#### Templates

Templates define how inputs are formatted for the LLM:

```yaml
templates:
  binary_qa:
    system: Answer the following question with YES or NO only.
    prompt: "Question: {input}"
    metrics:
      - binary_exact
  
  complex_qa:
    system: Provide a detailed answer to the following question.
    prompt: "Question: {input}\nPlease explain in detail."
    metrics:
      - qa_with_explanation
```

#### Matrix Configuration

The matrix defines parameter combinations to test:

```yaml
matrix:
  hyperparameters:
    model: [gpt-4o, gpt-3.5-turbo, claude-3-opus]
    temperature: [0.0, 0.7]
    max_tokens: [100, 500]
```

LLM Matrix will run each test case with every combination of these parameters.

#### Test Cases

Individual test cases define inputs and expected outputs:

```yaml
cases:
  - input: Is water wet?
    ideal: "YES"
    tags: [science, basic]
  
  - input: |
      What are the three primary colors?
    ideal: "The three primary colors are red, blue, and yellow."
    tags: [art]
    template: list_qa  # Override the default template
```

## Runner Configuration

You can customize the runner behavior with a separate config file:

```yaml
concurrency: 5  # Number of concurrent API calls
retries: 3      # Number of retry attempts for failed calls
timeout: 30     # Timeout in seconds for API calls
plugins:
  - citeseek    # Enable plugins
```

Pass this config to the CLI with:

```bash
llm-matrix run test-suite.yaml --runner-config runner-config.yaml
```

## Advanced Configuration

### Using Variables

You can use variables in your prompts:

```yaml
templates:
  complex_prompt:
    system: "You are an expert in {domain}."
    prompt: "Question about {domain}: {input}"
```

Then in your cases:

```yaml
cases:
  - input: What is DNA?
    ideal: "DNA is a molecule that carries genetic information..."
    variables:
      domain: genetics
```

### Tags for Analysis

Tags help organize and filter your results:

```yaml
cases:
  - input: What is photosynthesis?
    ideal: "Photosynthesis is a process used by plants..."
    tags: [biology, plants, difficulty:easy]
```

You can later filter or group results by these tags.

## Examples

See the [examples directory](https://github.com/monarch-initiative/llm-runner/examples) for complete examples of test suite configurations.
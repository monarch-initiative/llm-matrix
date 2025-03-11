# Evaluation Metrics

LLM Matrix provides various metrics to evaluate model responses against expected outputs. These metrics are specified in the template configuration.

## Available Metrics

### Basic Metrics

#### `binary_exact`

Evaluates binary (YES/NO) responses with exact matching.

```yaml
templates:
  binary_qa:
    system: Answer the following question with YES or NO only.
    prompt: "Question: {input}"
    metrics:
      - binary_exact
```

- Score: 1.0 for exact match, 0.0 otherwise
- Best for: Simple YES/NO questions where only the answer matters, not explanation

#### `qa_simple`

Simple string matching for question answering.

```yaml
metrics:
  - qa_simple
```

- Score: 1.0 for exact match, partial scores for close matches
- Best for: Factual questions with specific answers

### Explanation Metrics

#### `qa_with_explanation`

Evaluates both the answer and explanation.

```yaml
metrics:
  - qa_with_explanation
```

- Score: Combined score for answer correctness and explanation quality
- Best for: Questions requiring both correct answers and explanations

#### `binary_with_explanation`

For YES/NO questions with explanations.

```yaml
metrics:
  - binary_with_explanation
```

- Score: 1.0 for correct binary answer with good explanation, lower for partial matches
- Best for: Binary questions where explanation is important

### List Metrics

#### `list_comparison`

Compares lists of items.

```yaml
metrics:
  - list_comparison
```

- Score: Based on overlap between expected and actual lists
- Best for: Enumeration tasks (e.g., "List the planets in the solar system")

## Creating Custom Metrics

You can create custom metrics by implementing the `Metric` class:

```python
from llm_matrix.metrics import Metric
from llm_matrix.schema import EvalResult, TestCase, LLMResponse

class MyCustomMetric(Metric):
    def evaluate(self, case: TestCase, response: LLMResponse) -> EvalResult:
        # Implement your evaluation logic
        score = calculate_score(case.ideal, response.text)
        
        return EvalResult(
            score=score,
            explanation="Reason for this score"
        )
```

Register your custom metric:

```python
from llm_matrix.metrics import register_metric

register_metric("my_custom_metric", MyCustomMetric())
```

Then use it in your templates:

```yaml
templates:
  my_template:
    system: Custom prompt
    prompt: "{input}"
    metrics:
      - my_custom_metric
```

## Best Practices

- Choose metrics appropriate for your task type
- Consider using multiple metrics for complex tasks
- For binary tasks, prefer specialized binary metrics over general ones
- When using list-based metrics, ensure your ideal answer is formatted as expected
- For most accurate scoring, define clear evaluation criteria in your prompts

## Metrics API Reference

For detailed API documentation of all metrics, see the [Metrics API Reference](../api/metrics.md).
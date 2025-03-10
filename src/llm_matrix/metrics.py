import re
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type

from llm_matrix import LLMRunner
from llm_matrix.schema import TestCaseResult, MetricEnum, Response

logger = logging.getLogger(__name__)
DEFAULT_EVALUATION_MODEL_NAME = "gpt-4o"


class MetricEvaluator(ABC):
    """Base class for metric evaluators."""
    
    @abstractmethod
    def evaluate(
        self, 
        actual_output: str, 
        expected_output: str, 
        runner: Optional[LLMRunner] = None,
        result: Optional[TestCaseResult] = None
    ) -> float:
        """
        Evaluate the result and return a score between 0 and 1.
        
        :param actual_output: The actual output from the model
        :param expected_output: The expected output
        :param runner: The LLMRunner instance
        :param result: The TestCaseResult instance, for storing evaluation messages
        :return: A score between 0 and 1
        """
        pass


class QAWithExplanationEvaluator(MetricEvaluator):
    """Evaluator for QA with explanation metrics."""
    
    def evaluate(
        self, 
        actual_output: str, 
        expected_output: str, 
        runner: Optional[LLMRunner] = None,
        result: Optional[TestCaseResult] = None
    ) -> float:
        """Evaluate QA with explanation result."""
        # First token regex
        pattern = re.compile(r"^(\w+)")
        match = pattern.match(actual_output)
        actual_answer = match.group(1).upper() if match else "OTHER"
        
        expected_match = pattern.match(expected_output)
        if not expected_match:
            logger.warning(f"Could not extract first token from expected output: {expected_output}")
            return 0.0
        
        expected_answer = expected_match.group(1).upper()
        
        if actual_answer == expected_answer:
            score = 1.0
        elif actual_answer == "OTHER" or expected_answer == "OTHER":
            score = 0.5
        else:
            score = 0.0
            
        return score


class LLMBasedEvaluator(MetricEvaluator):
    """Base class for evaluators that use LLMs for scoring."""
    
    def __init__(self, system_prompt: str, user_input_template: str):
        self.system_prompt = system_prompt
        self.user_input_template = user_input_template
    
    def evaluate(
        self, 
        actual_output: str, 
        expected_output: str, 
        runner: Optional[LLMRunner] = None,
        result: Optional[TestCaseResult] = None
    ) -> float:
        """Evaluate using an LLM."""
        if not runner:
            logger.error("Runner is required for LLM-based evaluation")
            return 0.0
            
        eval_model = self._get_eval_model(runner)
        if not eval_model:
            logger.error("Could not get evaluation model")
            return 0.0
            
        eval_response = self._prompt_model(eval_model, actual_output, expected_output)
        eval_response_text = eval_response.text.strip()
        
        if result:
            result.evaluation_message = eval_response_text
            
        score = self._extract_score(eval_response_text)
        return score
    
    def _get_eval_model(self, runner: LLMRunner):
        """Get the evaluation model."""
        if runner.config and runner.config.evaluation_model_name:
            eval_model_name = runner.config.evaluation_model_name
        else:
            eval_model_name = DEFAULT_EVALUATION_MODEL_NAME
            
        return runner.get_aimodel({"model": eval_model_name})
    
    def _prompt_model(self, model, actual_output: str, expected_output: str):
        """Prompt the evaluation model."""
        user_input = self._format_user_input(actual_output, expected_output)
        
        return model.prompt(
            system_prompt=self.system_prompt,
            user_input=user_input
        )
    
    def _format_user_input(self, actual_output: str, expected_output: str) -> str:
        """Format the user input for the evaluation model."""
        return self.user_input_template.format(
            actual_output=actual_output,
            expected_output=expected_output
        )
    
    def _extract_score(self, response_text: str) -> float:
        """Extract a score from the LLM response."""
        pattern = re.compile(r"(\d+(\.\d+)?)")
        matches = pattern.match(response_text)
        
        if matches:
            return float(matches.group(1))
        else:
            logger.error(f"Could not parse score from {response_text}")
            raise ValueError(f"Could not parse score from {response_text}")


class ListMembershipEvaluator(LLMBasedEvaluator):
    """Evaluator for list membership metrics."""
    
    def __init__(self):
        super().__init__(
            system_prompt=(
                "Check if all the expected list items are present in the text. "
                "Your response should be an overlap score between 0 and 1, where 1 is a perfect "
                "match (all members match) and 0 is the worst possible match (no members match). "
                "Your response should be the score followed by any explanatory text. "
                "For example, '0.5 Only half of the items matched'. "
                "Do NOT put ANY text before the score. ALWAYS start with the score. "
                "Note the text you are evaluating may have additional verbiage, do not "
                "penalize this. Your task is just to determine if the list is presented clearly "
                "and if the items match"
            ),
            user_input_template=(
                "The expected list is: {expected_output}. "
                "The text: {actual_output}. "
            )
        )


class ReviewEvaluator(LLMBasedEvaluator):
    """Evaluator for review metrics."""
    
    def __init__(self):
        super().__init__(
            system_prompt=(
                "Review the output for correctness, completeness, and clarity. "
                "The response should be a score between 0 (worst) and 1 (best). "
                "Your response should be the score followed by any explanatory text. "
                "For example, '0.3 The response has many inaccuracies'. "
            ),
            user_input_template="The output to score is: {actual_output}. "
        )


class RankedListEvaluator(LLMBasedEvaluator):
    """Evaluator for ranked list metrics."""
    
    def __init__(self):
        super().__init__(
            system_prompt=(
                "Compare the ranked list to the expected output. "
                "The response should be a score between 0 and 1. "
                "If the item ranked first is equal to the expected item, score is 1. "
                "If there is no overlap between the ranked list and the expected list, score is 0. "
                "Otherwise score according to rank, with 0.5 for 2nd, 0.25 for 3rd, and so on."
            ),
            user_input_template=(
                "The expected answer is: {expected_output}. "
                "The output to score is: {actual_output}. "
            )
        )


class SimpleQuestionEvaluator(LLMBasedEvaluator):
    """Evaluator for simple question metrics."""
    
    def __init__(self):
        super().__init__(
            system_prompt=(
                "Compare the answer given to the expected output. "
                "The response should be a score between 0 and 1. "
                "The answer should be provided first, explanations may follow "
                "A precise correct answer is 1, a wrong answer is 0."
                "You can use values in between for imprecise answers"
            ),
            user_input_template=(
                "The expected answer is: {expected_output}. "
                "The output to score is: {actual_output}. "
            )
        )


# Registry of metric evaluators
METRIC_REGISTRY: Dict[str, MetricEvaluator] = {
    MetricEnum.QA_WITH_EXPLANATION.value: QAWithExplanationEvaluator(),
    MetricEnum.LIST_MEMBERSHIP.value: ListMembershipEvaluator(),
    MetricEnum.REVIEW.value: ReviewEvaluator(),
    MetricEnum.RANKED_LIST.value: RankedListEvaluator(),
    MetricEnum.SIMPLE_QUESTION.value: SimpleQuestionEvaluator(),
}


def register_metric_evaluator(metric_name: str, evaluator: MetricEvaluator) -> None:
    """
    Register a custom metric evaluator.
    
    :param metric_name: The name of the metric
    :param evaluator: The evaluator instance
    """
    METRIC_REGISTRY[metric_name] = evaluator


def evaluate_result(result: TestCaseResult, runner: Optional[LLMRunner] = None):
    """
    Evaluate the result of a test case.

    Example:

        >>> result = TestCaseResult(
        ...    case=TestCase(input="What is II+IV?", ideal="VI. Blah"),
        ...    response=Response(text="VI"),
        ...    hyperparameters={"model": "gpt-4o"},
        ...    metrics=["qa_with_explanation"],
        ... )
        >>> evaluate_result(result)
        >>> result.score
        1.0
        >>> result.response.text = "VII"
        >>> evaluate_result(result)
        >>> result.score
        0.0
        >>> result.response.text = "Other"
        >>> evaluate_result(result)
        >>> result.score
        0.5

    :param result: The test case result to evaluate
    :param runner: The LLMRunner instance
    """
    actual_output = result.response.text
    expected_output = result.case.ideal
    
    scores = []
    
    for metric_name in result.metrics or []:
        if metric_name not in METRIC_REGISTRY:
            raise NotImplementedError(f"Metric {metric_name} not implemented")
            
        evaluator = METRIC_REGISTRY[metric_name]
        try:
            score = evaluator.evaluate(
                actual_output=actual_output,
                expected_output=expected_output,
                runner=runner,
                result=result
            )
            scores.append(score)
        except Exception as e:
            logger.error(f"Error evaluating metric {metric_name}: {e}")
            # Optionally fall back to a default score
            # scores.append(0.0)
            # Or re-raise the exception
            raise
    
    if scores:
        result.score = sum(scores) / len(scores)

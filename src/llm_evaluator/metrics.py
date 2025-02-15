import re
from typing import Optional

from llm_evaluator import TestCase, LLMRunner
from llm_evaluator.schema import TestCaseResult, MetricEnum, Response

DEFAULT_EVALUATION_MODEL_NAME = "gpt-4o"

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

    :param result:
    :param runner:
    :return:
    """
    actual_output = result.response.text
    expected_output = result.case.ideal

    # for methods that use LLMs to eval
    if runner and runner.config and runner.config.evaluation_model_name:
        eval_model_name = runner.config.evaluation_model_name
    else:
        eval_model_name = DEFAULT_EVALUATION_MODEL_NAME
    eval_model = runner.get_aimodel({"model": eval_model_name}) if runner else None

    # TODO: use plugin mechanism
    scores = []
    for m in result.metrics:
        if m == MetricEnum.QA_WITH_EXPLANATION.value:
            # first token regex
            pattern = re.compile(r"^(\w+)")
            match = pattern.match(actual_output)
            actual_answer = match.group(1).upper() if match else "OTHER"
            expected_answer = pattern.match(expected_output).group(1).upper()
            if actual_answer == expected_answer:
                score = 1.0
            elif actual_answer == "OTHER" or expected_answer == "OTHER":
                score = 0.5
            else:
                score = 0.0
            scores.append(score)
        elif m == MetricEnum.LIST_MEMBERSHIP.value:
            if runner.config and runner.config.evaluation_model_name:
                eval_model_name = runner.config.evaluation_model_name
            else:
                eval_model_name = DEFAULT_EVALUATION_MODEL_NAME
            eval_model = runner.get_aimodel({"model": eval_model_name})
            eval_response = eval_model.prompt(
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
                user_input=(
                    f"The expected list is: {expected_output}. "
                    f"The text: {actual_output}. "
                ),
            )
            eval_response_text = eval_response.text.strip()
            result.evaluation_message = eval_response_text
            # use a regex
            pattern = re.compile(r"(\d+(\.\d+)?)")
            matches = pattern.match(eval_response_text)
            if matches:
                scores.append(float(pattern.match(eval_response_text).group(1)))
            else:
                raise ValueError(f"Could not parse score from {eval_response_text}")
        elif m == MetricEnum.REVIEW.value:
            # result.case.input
            eval_response = eval_model.prompt(
                system_prompt=(
                    "Review the output for correctness, completeness, and clarity. "
                    "The response should be a score between 0 (worst) and 1 (best). "
                    "Your response should be the score followed by any explanatory text. "
                    "For example, '0.3 The response has many inaccuracies'. "
                ),
                user_input=(
                    f"The output to score is: {actual_output}. "
                ),
            )
            eval_response_text = eval_response.text.strip()
            result.evaluation_message = eval_response_text
            # use a regex
            pattern = re.compile(r"(\d+(\.\d+)?)")
            matches = pattern.match(eval_response_text)
            if matches:
                scores.append(float(pattern.match(eval_response_text).group(1)))
            else:
                raise ValueError(f"Could not parse score from {eval_response_text}")
        elif m == MetricEnum.RANKED_LIST.value:
            eval_response = eval_model.prompt(
                system_prompt=(
                    "Compare the ranked list to the expected output. "
                    "The response should be a score between 0 and 1. "
                    "If the item ranked first is equal to the expected item, score is 1. "
                    "If there is no overlap between the ranked list and the expected list, score is 0. "
                    "Otherwise score according to rank, with 0.5 for 2nd, 0.25 for 3rd, and so on."
                ),
                user_input=(
                    f"The expected answer is: {expected_output}. "
                    f"The output to score is: {actual_output}. "
                ),
            )
            eval_response_text = eval_response.text.strip()
            result.evaluation_message = eval_response_text
            # use a regex
            pattern = re.compile(r"(\d+(\.\d+)?)")
            matches = pattern.match(eval_response_text)
            if matches:
                scores.append(float(pattern.match(eval_response_text).group(1)))
            else:
                raise ValueError(f"Could not parse score from {eval_response_text}")
        elif m == MetricEnum.SIMPLE_QUESTION.value:
            eval_response = eval_model.prompt(
                system_prompt=(
                    "Compare the answer given to the expected output. "
                    "The response should be a score between 0 and 1. "
                    "The answer should be provided first, explanations may follow "
                    "A precise correct answer is 1, a wrong answer is 0."
                    "You can use values in between for imprecise answers"
                ),
                user_input=(
                    f"The expected answer is: {expected_output}. "
                    f"The output to score is: {actual_output}. "
                ),
            )
            eval_response_text = eval_response.text.strip()
            result.evaluation_message = eval_response_text
            # use a regex
            pattern = re.compile(r"(\d+(\.\d+)?)")
            matches = pattern.match(eval_response_text)
            if matches:
                scores.append(float(pattern.match(eval_response_text).group(1)))
            else:
                raise ValueError(f"Could not parse score from {eval_response_text}")
        else:
            raise NotImplementedError(f"Metric {m} not implemented")
    if scores:
        result.score = sum(scores) / len(scores)

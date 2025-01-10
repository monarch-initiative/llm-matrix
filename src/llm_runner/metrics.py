import re

from llm_runner import TestCase
from llm_runner.schema import TestCaseResult, MetricEnum, Response


def evaluate_result(result: TestCaseResult):
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
    :return:
    """
    actual_output = result.response.text
    expected_output = result.case.ideal
    if MetricEnum.QA_WITH_EXPLANATION.value in result.metrics:
        # first token regex
        pattern = re.compile(r"^(\w+)")
        actual_answer = pattern.match(actual_output).group(1).upper()
        expected_answer = pattern.match(expected_output).group(1).upper()
        if actual_answer == expected_answer:
            result.score = 1.0
        elif actual_answer == "OTHER" or expected_answer == "OTHER":
            result.score = 0.5
        else:
            result.score = 0.0
    else:
        raise NotImplementedError("Metric not implemented")

import pytest

from llm_eval import load_suite, Suite
from tests.conftest import INPUT_DIR


@pytest.mark.parametrize("example", [
    "test-eval"
    ])
def test_model(example: str):
    path = INPUT_DIR / f"{example}.yaml"
    suite = load_suite(path)
    assert isinstance(suite, Suite)

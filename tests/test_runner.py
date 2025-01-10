import pytest

from llm_runner import load_suite, Suite, LLMRunner
from tests.conftest import INPUT_DIR, STORE_PATH


@pytest.mark.parametrize("example", [
    "test-eval"
    ])
def test_runner(example: str):
    path = INPUT_DIR / f"{example}.yaml"
    suite = load_suite(path)
    runner = LLMRunner(store_path=STORE_PATH)
    for case in suite.cases:
        t = runner.get_template(case, suite)
        assert t is not None, f"Template not found for {case}"
    results = runner.run(suite)
    for r in results:
        print(r.model_dump_json(indent=2))


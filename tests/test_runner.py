from pathlib import Path

import pytest

from llm_eval import load_suite, Suite, LLMRunner
from tests.conftest import INPUT_DIR, STORE_PATH


@pytest.mark.parametrize("example,store_path", [
    ("test-eval", STORE_PATH),
    ("bacterial-proteins", STORE_PATH),
    ])
def test_runner(example: str, store_path: Path):
    path = INPUT_DIR / f"{example}.yaml"
    suite = load_suite(path)
    runner = LLMRunner(store_path=store_path)
    for case in suite.cases:
        t = runner.get_template(case, suite)
        assert t is not None, f"Template not found for {case}"
    results = runner.run(suite)
    for r in results:
        print(r.model_dump_json(indent=2))


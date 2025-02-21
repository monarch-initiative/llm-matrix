from pathlib import Path

import pytest

from llm_matrix import load_suite, Suite, LLMRunner, TestCase
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
        assert r.score is not None

def test_generate_ideal():
    suite = Suite(
        name="test-gen-ideal",
        cases=[TestCase(input="choose a random color",)],
        matrix={"hyperparameters": {"model": ["gpt-4o", "gpt-4o-mini"],
                                    "temperature": [0, 0.01, 0.02]}},

    )
    runner = LLMRunner()
    results = runner.run(suite)
    for r in results:
        print(r.model_dump_json(indent=2))
        assert r.score is None




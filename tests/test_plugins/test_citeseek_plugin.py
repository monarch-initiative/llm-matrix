from pathlib import Path

import pytest

from llm_eval import load_suite, LLMRunner
from llm_eval.plugins.citeseek_plugin import CiteseekPlugin
from tests.conftest import INPUT_DIR


def test_citeseek_plugin():
    citeseek = CiteseekPlugin()
    assert citeseek is not None
    resp = citeseek.prompt("Pex1 gene involved in peroxisome biogenesis")
    print(resp.text)

@pytest.mark.parametrize("example", [
    "test-citeseek"
    ])
def test_runner_with_plugin(example: str):
    path = INPUT_DIR / f"{example}.yaml"
    suite = load_suite(path)
    assert suite.models is not None
    assert suite.models["citeseek-gpt-4o"] is not None
    runner = LLMRunner(store_path=Path("foo.db"))
    for case in suite.cases:
        t = runner.get_template(case, suite)
        assert t is not None, f"Template not found for {case}"
    results = runner.run(suite)
    for r in results:
        print(r.model_dump_json(indent=2))
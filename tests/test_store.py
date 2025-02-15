import json
from copy import deepcopy

import pytest
from databricks.sdk.retries import retried
from llm_evaluator.store import Store
from llm_evaluator.schema import TestCaseResult, Response, Suite, TestCase

from tests.conftest import INPUT_DIR


@pytest.mark.parametrize("original_input", [
    {"a": 1},
    {
        "sources": [
            {
                "name": "n",
            },
            {
                "url": "u2",
            }
        ]
    },
    None,
])
@pytest.mark.parametrize("input_text,ideal", [
    ("1+1", "2"),
    ("1+3", "4"),
    ("open-ended", None),
])
def test_store(original_input: dict, input_text, ideal: str):
    path = INPUT_DIR / "test-cache.db"
    path.unlink(missing_ok=True)
    store = Store(path)
    assert store.size == 0
    case1 = TestCase(input=input_text, ideal=ideal, original_input=original_input)
    suite = Suite(name="test", cases=[case1], matrix={"hyperparameters": {}})
    response = Response(text=ideal) if ideal else Response(text="foo")
    result = TestCaseResult(case=suite.cases[0], response=response, hyperparameters={"model": "gpt-4"})
    assert store.get_result(suite, suite.cases[0], {"model": "gpt-4"}) is None
    store.add_result(suite, result)
    cached = store.get_result(suite, suite.cases[0], {"model": "gpt-4"})
    assert cached.response == response
    assert store.size == 1
    assert store.get_result(suite, suite.cases[0], {}) is None
    modified_result = deepcopy(result)
    modified_result.response.text = "3"
    store.add_result(suite, modified_result)
    # PK was not modified
    assert store.size == 1
    cached = store.get_result(suite, suite.cases[0], {"model": "gpt-4"})
    assert cached.response.text == "3"
    new_result = deepcopy(result)
    new_result.case.ideal = "3"
    store.add_result(suite, new_result)
    assert store.size == 2
    modified_hyp_result = deepcopy(result)
    modified_hyp_result.hyperparameters["model"] = "gpt-5"
    store.add_result(suite, modified_hyp_result)
    assert store.size == 3




@pytest.mark.parametrize("obj", [
    {"a": 1, "b": 2},
    [{"a": 1}, {"a": 2}],
    [
            {
                "a": 1,
            },
            {
                "b": 2,
            },
    ],
    {},
])
@pytest.mark.parametrize("pre_serialize", [True, False])
def test_duckdb(obj, pre_serialize):
    """
    https://stackoverflow.com/questions/79407620/what-is-the-correct-way-to-insert-into-the-duckdb-json-type-via-the-python-api

    :param obj:
    :param pre_serialize:
    :return:
    """
    pytest.skip("Known failure")
    import duckdb
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE test (obj JSON)")
    if pre_serialize:
        obj_to_insert = json.dumps(obj)
    else:
        obj_to_insert = obj
    conn.execute("INSERT INTO test VALUES (?)", (obj_to_insert,))
    result = conn.execute("SELECT * FROM test").fetchone()
    retrieved_obj = json.loads(result[0])
    assert retrieved_obj == obj
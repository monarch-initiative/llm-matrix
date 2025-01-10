import logging
from copy import copy
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Dict, Any, Optional, Iterator, List

from llm_runner import Suite, Matrix, AIModel, Template
from llm_runner.metrics import evaluate_result
from llm_runner.schema import TestCaseResult, StrictBaseModel
from llm_runner.store import Store
from llm_runner.utils import iter_hyperparameters

logger = logging.getLogger(__name__)

class LLMRunnerConfig(StrictBaseModel):
    model_name_map: Optional[Dict[str, str]] = None

@dataclass
class LLMRunner:

    store_path: Optional[Path] = None
    _aimodels: Optional[Dict[tuple, AIModel]] = None
    _store: Optional[Store] = None
    config: Optional[LLMRunnerConfig] = None

    def run(self, suite: Suite) -> List[TestCaseResult]:
        """
        Run the test suite.

        :param suite:
        :return:
        """
        return list(self.run_iter(suite))

    def run_iter(self, suite: Suite) -> Iterator[TestCaseResult]:
        """
        Run the test suite iterating over the results.

        :param suite:
        :return:
        """
        logger.info(f"Running suite {suite.name}")
        for params in iter_hyperparameters(suite.matrix):
            for case in suite.cases:
                result = self.run_case(case, params, suite)
                yield result

    def run_case(self, case, params: Dict[str, Any], suite: Suite) -> TestCaseResult:
        logger.info(f"Running case {case.input} with {params}")
        store = self._get_store()
        cached = store.get_result(suite.name, case, params)
        if cached:
            return cached
        actual_params = copy(params)
        if self.config and "model" in params:
            model_logical_name = params["model"]
            actual_params["model"] = self.config.model_name_map.get(model_logical_name, model_logical_name)
            logger.info(f"Mapping model {model_logical_name} to {actual_params['model']}")
        model = self.get_aimodel(params)
        template = self.get_template(case, suite)
        response = model.prompt(case.input, template=template)
        result = TestCaseResult(
            case=case,
            response=response,
            hyperparameters=params,
            metrics=template.metrics,
        )
        evaluate_result(result)
        store.add_result(suite.name, result)
        return result

    def get_template(self, case, suite: Suite) -> Optional[Template]:
        tn = case.template
        if not tn:
            tn = suite.template
        if not tn:
            return None
        return suite.templates[tn]

    def get_aimodel(self, params: Dict[str, Any]) -> AIModel:
        if not self._aimodels:
            self._aimodels = {}
        key = tuple(sorted(params.items()))
        if key not in self._aimodels:
            self._aimodels[key] = AIModel(parameters=params)
        return self._aimodels[key]

    def _get_store(self) -> Store:
        if not self._store:
            if not self.store_path:
                self.store_path = Path("results") / "cache.db"
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self._store = Store(self.store_path)
        return self._store


import logging
from copy import copy
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Dict, Any, Optional, Iterator, List

from llm_matrix import Suite, Matrix, AIModel, Template, TestCase
from llm_matrix.schema import TestCaseResult, StrictBaseModel
from llm_matrix.store import Store
from llm_matrix.utils import iter_hyperparameters

logger = logging.getLogger(__name__)

class LLMRunnerConfig(StrictBaseModel):
    model_name_map: Optional[Dict[str, str]] = None
    evaluation_model_name: Optional[str] = None

@dataclass
class LLMRunner:

    store_path: Optional[Path] = None
    _aimodels: Optional[Dict[tuple, AIModel]] = None
    _store: Optional[Store] = None
    config: Optional[LLMRunnerConfig] = None

    def run(self, suite: Suite) -> List[TestCaseResult]:
        """
        Run the suite of cases

        :param suite:
        :return:
        """
        return list(self.run_iter(suite))

    def run_iter(self, suite: Suite) -> Iterator[TestCaseResult]:
        """
        Run the suite of cases iterating over the results.

        :param suite:
        :return:
        """
        logger.info(f"Running suite {suite.name}")
        for params in iter_hyperparameters(suite.matrix):
            logger.info(f"Running {len(suite.cases)} with {params}")
            for n, case in enumerate(suite.cases):
                logger.debug(f"Running case {n+1}/{len(suite.cases)}")
                result = self.run_case(case, params, suite)
                yield result

    def run_case(self, case: TestCase, params: Dict[str, Any], suite: Suite) -> TestCaseResult:
        logger.info(f"Running case {case.input} with {params}")
        store = self._get_store()
        cached = store.get_result(suite, case, params)
        if cached:
            return cached
        actual_params = copy(params)
        if self.config and "model" in params:
            model_logical_name = params["model"]
            actual_params["model"] = self.config.model_name_map.get(model_logical_name, model_logical_name)
            logger.info(f"Mapping model {model_logical_name} to {actual_params['model']}")
        model = self.get_aimodel(actual_params, suite=suite)
        template = self.get_template(case, suite)
        response = model.prompt(case.input, template=template, case=case)
        result = TestCaseResult(
            case=case,
            response=response,
            hyperparameters=params,
            metrics=template.metrics if template else None,
        )
        from llm_matrix.metrics import evaluate_result
        evaluate_result(result, runner=self)
        store.add_result(suite, result)
        return result

    def get_template(self, case, suite: Suite) -> Optional[Template]:
        tn = case.template
        if not tn:
            tn = suite.template
        if not tn:
            return None
        return suite.templates[tn]

    def get_aimodel(self, params: Dict[str, Any], suite: Suite=None) -> AIModel:
        if not self._aimodels:
            self._aimodels = {}
        key = tuple(sorted(params.items()))
        if key not in self._aimodels:
            if suite and suite.models:
                bespoke_models = suite.models
                model_name = params.get("model")
                if model_name and model_name in bespoke_models:
                    model_info = bespoke_models[model_name]
                    params = {**params, **model_info.parameters}
                    plugins = model_info.plugins or []
                    # TODO: proper mechanism for plugins
                    if "citeseek" in plugins:
                        from llm_matrix.plugins.citeseek_plugin import CiteseekPlugin
                        self._aimodels[key] = CiteseekPlugin(parameters=params)
            if key not in self._aimodels:
                self._aimodels[key] = AIModel(parameters=params)
        m = self._aimodels[key]
        return self._aimodels[key]

    def _get_store(self) -> Store:
        if not self._store:
            if not self.store_path:
                self.store_path = Path("results") / "cache.db"
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self._store = Store(self.store_path)
        return self._store


import logging
from typing import Any, Dict, Optional

import llm
from IPython.core.debugger import prompt
from pydantic import ConfigDict, Field

from llm_runner import TestCase
from llm_runner.schema import StrictBaseModel, Template, Response

logger = logging.getLogger(__name__)

RESERVED = ["model", "key"]

DEFAULT_MODEL = "gpt-4o"

class AIModel(StrictBaseModel):
    """
    A model that uses the LLM library to generate responses.

    Example:

        >>> from llm_runner import AIModel
        >>> model = AIModel(parameters={"model": "gpt-4o"})
        >>> response = model.prompt("What is 1+1?")
        >>> assert "2" in response.text

    With a template

        >>> from llm_runner import AIModel, Template
        >>> template = Template(
        ...     system="Answer the question with a single number, no other text",
        ...     prompt="What is the value of {input}?",
        ... )
        >>> model = AIModel(parameters={"model": "gpt-4o"})
        >>> response = model.prompt("1+1", template=template)
        >>> print(response.text)
        2
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    parameters: Optional[Dict[str, Any]] = Field({}, description="The parameters of the model")
    llm_model: Optional[llm.Model] = Field(None, description="The LLM model")

    def _prompt_parameters(self):
        return {k: v for k, v in self.parameters.items() if k not in RESERVED}

    @property
    def ensure_llm_model(self) -> llm.Model:
        if not self.llm_model:
            parameters = self.parameters or {}
            model = llm.get_model(parameters.get("model", DEFAULT_MODEL))
            if model.needs_key:
                model.key = llm.get_key(None, model.needs_key, model.key_env_var)
            self.llm_model = model
            logger.info(f"Loaded model {model.name}")
        return self.llm_model

    def prompt(self, user_input: str, template: Optional[Template] = None, system_prompt: Optional[str] = None, extra_system_prompt: Optional[str] = None, case: Optional[TestCase]=None, **kwargs) -> Response:
        m = self.ensure_llm_model
        template_params = {"input": user_input}
        if case and case.original_input:
            template_params.update(case.original_input)
        if template:
            if template.system:
                system_prompt = template.system.format(**template_params)
            else:
                system_prompt = None
            main_prompt = template.prompt.format(**template_params)
        else:
            main_prompt = user_input
        if extra_system_prompt:
            if not system_prompt:
                system_prompt = extra_system_prompt
            else:
                system_prompt = f"{system_prompt}\n{extra_system_prompt}"
        prompt_params = self._prompt_parameters()
        logger.debug(f"Prompting with MAIN: {main_prompt} SYS:{system_prompt} P: {prompt_params}")
        # print(f"Prompting with MAIN: {main_prompt} SYS:{system_prompt} P: {prompt_params}")
        r = m.prompt(main_prompt, system=system_prompt, **prompt_params)
        return Response(text=r.text(), prompt=main_prompt, system=system_prompt)


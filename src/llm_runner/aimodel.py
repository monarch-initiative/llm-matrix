import logging
from typing import Any, Dict, Optional

import llm
from IPython.core.debugger import prompt
from pydantic import ConfigDict, Field

from llm_runner.schema import StrictBaseModel, Template, Response

logger = logging.getLogger(__name__)

RESERVED = ["model", "key"]

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
    parameters: Optional[Dict[str, Any]] = Field(..., description="The parameters of the model")
    llm_model: Optional[llm.Model] = Field(None, description="The LLM model")

    def _prompt_parameters(self):
        return {k: v for k, v in self.parameters.items() if k not in RESERVED}

    @property
    def ensure_llm_model(self) -> llm.Model:
        if not self.llm_model:
            model = llm.get_model(self.parameters.get("model"))
            if model.needs_key:
                model.key = llm.get_key(None, model.needs_key, model.key_env_var)
            self.llm_model = model
            logger.info(f"Loaded model {model.name}")
        return self.llm_model

    def prompt(self, user_input: str, template: Optional[Template] = None, system_prompt: str = None) -> Response:
        m = self.ensure_llm_model
        if template:
            system_prompt = template.system.format(input=user_input)
            main_prompt = template.prompt.format(input=user_input)
        else:
            main_prompt = user_input
        prompt_params = self._prompt_parameters()
        r = m.prompt(main_prompt, system=system_prompt, **prompt_params)
        return Response(text=r.text(), prompt=main_prompt, system=system_prompt)


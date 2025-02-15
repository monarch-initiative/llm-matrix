import os
import subprocess
from typing import Optional


from llm_eval import AIModel, Template
from llm_eval.schema import Response

EXTRA_SYSTEM = """
When forming your response, make use of any relevant information from the abstracts below.

If you do make use of this information, provide citations of the form [PMID:nnn] to
indicate where the information came from in your explanation.

Here are the potentially relevant abstracts:
"""

def search_pubmed(query: str) -> str:
    """
    Search pubmed for a query
    """
    cmd = ["/usr/local/bin/pubmed-search", query]
    #cmd = f"/usr/local/bin/curategpt pubmed search '{query}'"
    result = subprocess.run(
        cmd,
        #shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # Return string instead of bytes
        check=True  # Raise exception if command fails
    )
    return result.stdout


class CiteseekPlugin(AIModel):
    """
    Wraps CurateGPT citeseek.

    Note: until curategpt is easier to install, this needs a script called

    "pubmed-search" to be in /usr/local/bin

    Example:

        .. code-block:: bash

            #!/bin/bash
            arch -arm64 /usr/local/bin/curategpt pubmed search "$@"


    """
    def prompt(self, user_input: str, template: Optional[Template] = None, system_prompt: str = None, **kwargs) -> Response:
        abstracts_str = search_pubmed(user_input)
        lines = [line for line in abstracts_str.split("\n") if not line.startswith("##")]
        abstracts_str = "\n".join(lines)
        extra_system = EXTRA_SYSTEM + "\n" + abstracts_str
        return super().prompt(user_input,
                              template=template,
                              system_prompt=system_prompt,
                              extra_system_prompt=extra_system)






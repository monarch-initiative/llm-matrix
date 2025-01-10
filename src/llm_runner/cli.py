"""
Command-line interface (CLI) for llm-runner.

To get a list of all commands:

```bash
llm-runner --help
```

Note that an easy way to use the CLI is via pipx:

```bash
pipx run llm-runner --help
```
"""
import logging
from pathlib import Path
from typing import Annotated, List, Optional

import typer
import yaml
from typer.main import get_command

from llm_runner import load_suite, LLMRunner
from llm_runner.runner import LLMRunnerConfig
from llm_runner.schema import results_to_dataframe

logger = logging.getLogger()

app = typer.Typer()

output_file_option = typer.Option(None, "--output-file", "-o", help="Output file path")

def configure_logging(verbosity: int):
    """Configure logging based on verbosity level"""
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Set up logger
    logger.setLevel(level)
    logger.addHandler(handler)

# This callback runs before any subcommand
@app.callback()
def main(
    verbose: Optional[int] = typer.Option(0, "--verbose", "-v", count=True),
):
    """
    Global options that can be used before any subcommand
    """
    configure_logging(verbose)

@app.command()
def run(
    suite_path: Path = typer.Argument(
                                      ...,
                                      exists=True,
                                      help="Path to the eval suite yaml"
                                      ),
    store_path: Optional[Path] = typer.Option(
        None,
        "--store-path", "-s",
        help="Path to the store"
    ),
    runner_config_path: Optional[Path] = typer.Option(
        None,
        "--runner-config",
        "-C",
        help="Path to the runner config"
    ),
    output_file: Optional[Path] = output_file_option,
):
    """
    Run the evaluation suite.
    """
    suite = load_suite(suite_path)
    runner_config = None
    if runner_config_path:
        with open(runner_config_path) as f:
            runner_config = LLMRunnerConfig(**yaml.safe_load(f))
    runner = LLMRunner(store_path=store_path, config=runner_config)
    results = []
    for r in runner.run_iter(suite):
        results.append(r)
        print(f"{r.score} {r.case.input} :: {r.response.text}")
    df = results_to_dataframe(results)
    print(df.describe())
    if output_file:
        with open(output_file, "w") as f:
            df.to_csv(f, index=False, sep="\t")
        typer.echo(f"Conversion result written to {output_file}")


# DO NOT REMOVE THIS LINE
# added this for mkdocstrings to work
# see https://github.com/bruce-szalwinski/mkdocs-typer/issues/18
click_app = get_command(app)
click_app.name = "llm-runner"

if __name__ == "__main__":
    app()

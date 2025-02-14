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
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Annotated, List, Optional

import pandas as pd
import typer
import yaml
from typer.main import get_command

from llm_runner import LLMRunner
from llm_runner.runner import LLMRunnerConfig
from llm_runner.schema import results_to_dataframe, load_suite

logger = logging.getLogger()

app = typer.Typer()

output_file_option = typer.Option(None, "--output-file", "-o", help="Output file path")
output_dir_option = typer.Option(None, "--output-dir", "-D", help="Output directory path")

class FormatEnum(str,  Enum):
    csv = "csv"
    tsv = "tsv"
    excel = "excel"
    jsonl = "jsonl"
    json = "json"
    yaml = "yaml"

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
def convert(
        input_files: List[Path] = typer.Argument(
                                      ...,
                                      exists=True,
                                      help="Path to files to be converted"
                                      ),
        source_field: Optional[str] = typer.Option(..., "-s", "--source"),
        target_field: Optional[str] = typer.Option(..., "-t", "--target"),

):
    """
    Converts input files

    :param input_files:
    :return:
    """
    dfs = [pd.read_csv(fn) for fn in input_files]
    df = pd.concat(dfs)
    for _, row in df.iterrows():
        x = {}


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
        help="Path to the cache store. Defaults to same directory as suite with .db extension"
    ),
    runner_config_path: Optional[Path] = typer.Option(
        None,
        "--runner-config",
        "-C",
        help="Path to the runner config"
    ),
    output_file: Optional[Path] = output_file_option,
    output_directory: Optional[Path] = output_dir_option,
    output_format: str = typer.Option(
        "tsv",
        "--output-format",
        "-F",
        help="Output format",

    ),
):
    """
    Run the evaluation suite.

    Example:

        llm-runner run my-conf.yaml

    """
    suite = load_suite(suite_path)
    if not store_path:
        store_path = suite_path.parent / (str(suite_path.stem) + ".db")
    if not output_directory:
        output_directory = suite_path.parent / (str(suite_path.stem) + "-output")
    runner_config = None
    if runner_config_path:
        with open(runner_config_path) as f:
            runner_config = LLMRunnerConfig(**yaml.safe_load(f))
    runner = LLMRunner(store_path=store_path, config=runner_config)
    results = []
    source_keys = set()
    for r in runner.run_iter(suite):
        results.append(r)
        print(f"## {r.score} {r.case.input} :: ideal= {r.case.ideal} :: resp= {r.response.text}")
        print(yaml.dump(r.model_dump()))
        if r.case.original_input:
            source_keys.update(r.case.original_input.keys())
    df = results_to_dataframe(results)
    typer.echo(df.describe())
    if output_file:
        if output_format == FormatEnum.excel:
            df.to_excel(output_file, index=False)
        elif output_format == FormatEnum.jsonl:
            with open(output_file, "w") as f:
                for r in results:
                    f.write(r.model_dump_json() + "\n")
        elif output_format == FormatEnum.json:
            with open(output_file, "w") as f:
                f.write(json.dumps([r.model_dump() for r in results]))
        elif output_format == FormatEnum.yaml:
            with open(output_file, "w") as f:
                yaml.safe_dump([r.model_dump() for r in results], f)
        elif output_format == FormatEnum.tsv:
            df.to_csv(output_file, index=False, sep="\t")
        elif output_format == FormatEnum.csv:
            df.to_csv(output_file, index=False)
        else:
            raise ValueError(f"Invalid output format {output_format}")
        typer.echo(f"Conversion result written to {output_file}")
    if output_directory:
        output_directory.mkdir(exist_ok=True, parents=True)
        df.to_csv(output_directory / "results.csv", index=False)
        #df.to_excel(output_directory / "results.xslx", index=False)
        df.to_html(output_directory / "results.html", index=False)
        df.describe().to_csv(output_directory / "summary.csv", index=True)
        #df.describe().to_excel(output_directory / "summary.xlsx", index=True)
        df.describe().to_html(output_directory / "summary.html", index=True)

        # by model
        grouped_by_model = df.groupby("model").aggregate(
            {"score": ["mean", "std", "max", "min", "count"]},
        )
        grouped_by_model.reset_index(inplace=True, drop=False, col_level=1)
        grouped_by_model.sort_values([("score", "mean")], ascending=False, inplace=True)
        print(grouped_by_model)
        grouped_by_model.to_csv(output_directory / "by_model.csv", index=False)

        # by (model, ideal)
        grouped_by_model_ideal = df.groupby(["model", "case_ideal"]).aggregate(
            {"score": ["mean", "std", "max", "min", "count"]},
        )
        grouped_by_model_ideal.reset_index(inplace=True, drop=False, col_level=1)
        grouped_by_model_ideal.sort_values([("score", "mean")], ascending=False, inplace=True)
        print(grouped_by_model_ideal)
        grouped_by_model_ideal.to_csv(output_directory / "by_model_ideal.csv", index=False)


        grouped_by_input = df.groupby("case_input").aggregate(
            {"score": ["mean", "std", "max", "min", "count"]},
        )
        grouped_by_input.reset_index(inplace=True, drop=False, col_level=1)
        grouped_by_input.sort_values([("score", "mean")], ascending=False, inplace=True)
        # Create the quantitative aggregations (across all models)
        score_agg = df.groupby("case_input").agg({
            "score": ["mean", "std", "max", "min", "count"]
        })

        # Create the response text pivot
        text_pivot = df.pivot_table(
            index="case_input",
            columns="hyperparameters",
            values="response_text",
            aggfunc="first"  # Takes the first response for each model
        )

        # Create the score pivot
        score_pivot = df.pivot_table(
            index="case_input",
            columns="hyperparameters",
            values="score",
            aggfunc="first"  # Takes the first response for each model
        )

        other_cols = df.groupby("case_input").agg({
            "case_ideal": "first",
            **{k: "first" for k in source_keys},
        })

        # Rename text columns to be clear they're responses
        text_pivot.columns = [f"{col}_response" for col in text_pivot.columns]

        # Flatten the score column names
        score_agg.columns = [f"{col[1]}" for col in score_agg.columns]

        # Combine the aggregations
        grouped_by_input = pd.concat([score_agg, text_pivot, score_pivot, other_cols], axis=1)
        grouped_by_input.sort_values("mean", ascending=False, inplace=True)
        grouped_by_input.to_csv(output_directory / "grouped_by_input.tsv", index=True, sep="\t")
        grouped_by_input.to_excel(output_directory / "grouped_by_input.xlsx", index=True)
        typer.echo(f"Conversion result written to {output_directory}")



# DO NOT REMOVE THIS LINE
# added this for mkdocstrings to work
# see https://github.com/bruce-szalwinski/mkdocs-typer/issues/18
click_app = get_command(app)
click_app.name = "llm-runner"

if __name__ == "__main__":
    app()

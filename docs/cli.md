# Command Line Interface

LLM Matrix provides a command-line interface for running evaluations and managing results.

## Basic Usage

```bash
llm-matrix run my-suite.yaml
```

## Global Options

```
--verbose, -v      Increase verbosity (can be used multiple times)
--help             Show help message and exit
```

## Commands

### `run`

Run a test suite against specified models.

```bash
llm-matrix run <suite-path> [options]
```

#### Arguments

- `suite-path`: Path to the evaluation suite YAML file

#### Options

- `--store-path, -s <path>`: Path to the cache store (defaults to same directory as suite with .db extension)
- `--runner-config, -C <path>`: Path to the runner config file
- `--output-file, -o <path>`: Path to save output file
- `--output-dir, -D <path>`: Directory to save output files (defaults to suite-name-output)
- `--output-format, -F <format>`: Output format (csv, tsv, excel, jsonl, json, yaml)

#### Examples

```bash
# Basic usage
llm-matrix run my-suite.yaml

# Specify custom output location
llm-matrix run my-suite.yaml -D ./results

# Use custom runner configuration
llm-matrix run my-suite.yaml -C runner-config.yaml

# Increase verbosity for debugging
llm-matrix run my-suite.yaml -vv

# Output as Excel file
llm-matrix run my-suite.yaml -o results.xlsx -F excel
```

### `convert`

Convert between different file formats.

```bash
llm-matrix convert <input-files> [options]
```

#### Arguments

- `input-files`: Paths to files to be converted

#### Options

- `--source, -s <field>`: Source field
- `--target, -t <field>`: Target field

## Output Formats

LLM Matrix supports the following output formats:

- `csv`: Comma-separated values
- `tsv`: Tab-separated values
- `excel`: Microsoft Excel format (requires the `excel` extra)
- `jsonl`: JSON Lines format (one JSON object per line)
- `json`: Single JSON array with all results
- `yaml`: YAML format

## Output Directory Structure

When using the default output directory, LLM Matrix creates:

```
suite-name-output/
├── by_model.csv             # Performance summary by model
├── by_model_ideal.csv       # Performance by model and ideal answer
├── grouped_by_input.tsv     # Detailed view of each test case
├── grouped_by_input.xlsx    # Excel version of the above
├── results.csv              # Raw results
├── results.html             # HTML view of raw results
├── summary.csv              # Statistical summary
└── summary.html             # HTML view of summary
```
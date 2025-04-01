# Introduction

This document is a brief introduction to the interfaces involved in building datasets,please refer to the detailed 👉[contribution demo](contribution-demo.md) for more information.

This interfaces including three modules:
* Multi-SWE-Bench data collection module
* Multi-SWE-Bench dataset construction module
* Multi-SWE-Bench report generation Module

The following sections describe the use of each module in turn !

# Getting started

## Install from Source

```bash
git clone https://github.com/multi-swe-bench/multi-swe-bench.git
cd multi-swe-bench

# Install dependencies
pip install -r requirements.txt
```

## 1.Multi-SWE-Bench data collection module

This module is used to automate the collection of software engineering benchmark datasets, primarily Pull Requests containing issue fixes and their associated Issues from GitHub repositories.

### Usage

```bash
python -m multi_swe_bench.collect.get_pipeline \
    --out_dir <your_output_dir_path> \
    --org <ORG> \         # organization name，For example: python
    --repo <REPO> \       # repository name，For example: cpython
    --tokens <your_github_tokens>    # Github tokens
```

### workflow

1. Get all Pull Requests
2. Filter valid PRs (closed and associated Issues)
3. Collect associated Issues
4. Merge the PR and Issue data.
5. Generate the final raw dataset

**Example of a generated file:**

```
your_output_dir/
├── <ORG>__<REPO>_prs.jsonl             
├── <ORG>__<REPO>_filtered_prs.jsonl    
├── <ORG>__<REPO>_related_issues.jsonl  
└── <ORG>__<REPO>_dataset.jsonl         # Raw data of the PR
```

## 2.Multi-SWE-Bench dataset building module

This is a module for building and processing Multi-SWE-Bench datasets.

### Usage

```bash
python -m multi_swe_bench.harness.build_dataset [Arguments]
```

### Main parameters

- `-mode`: Run mode, optional:
  - `-dataset`: build the full dataset (default), including building the image, running the instance and analyzing it, and generating the final report.
  - `instance`: build the image and run it.
  - `instance_only`: run instance only
  - `-image`: build image only

- `--workdir`: path to the working directory, where files related to the image and instance will be placed.
- `--raw_dataset_files`: path to raw dataset files collected from github (glob mode supported)
- `--output_dir`: path to the output directory, where the final dataset and reports will be located
- `--repo_dir`: path to the repository directory, where the automatically downloaded repositories will be stored.
- `--config`: Load configuration from json, toml or yaml file.

### Optional parameters

- `-force_build`: Whether to force a rebuild of the image (default: False)
- `--specifics`: Specify specific items to be processed
- `--skips`: Specify which items to skip
- `--need_clone`: If or not need to clone the repository (default: True), pull from github if True, otherwise copy locally.
- `--global_env`: Global environment variable settings.
- `-clear_env`: Clear environment variables (default: True)
- `--stop_on_error`: whether to stop on error (default: True)

### Performance-related parameters

- `-max_workers`: Maximum number of worker threads (default: 8)
- `-max_workers_build_image`: Maximum number of worker threads to build an image (default: 8)
- `-max_workers_run_instance`: Maximum number of worker threads to run an instance (default: 8)

### Logging related parameters

- `--log_dir`: Path to the log directory.
- `--log_level`: log level (default: INFO)
- `--log_to_console`: Whether to output logs to the console (default: True)

### Example

```bash
python -m multi_swe_bench.harness.build_dataset --config <your_config_file_path>
```

example_config:

```json
{
    "mode": "dataset",
    "workdir": "./tmp/workdir",
    "raw_dataset_files": [
        "./tmp/raw_dataset/*.jsonl"
    ],
    "force_build": false,
    "output_dir": "./tmp/dataset",
    "specifics": [],
    "skips": [],
    "repo_dir": "./tmp/repos",
    "need_clone": false,
    "global_env": [],
    "clear_env": true,
    "stop_on_error": true,
    "max_workers": 2,
    "max_workers_build_image": 8,
    "max_workers_run_instance": 8,
    "log_dir": "./tmp/logs",
    "log_level": "DEBUG"
}
```

**Example of a generated file:**

```
your_workdir/
├── <ORG_1>         	# Github organization name
|   └── <REPO_1>    	# Github repository name
|	  ├── images  	# Files and logs related to BASE and PR images
|	  └── instances	# Instances run-related logs
├── <ORG_2>         	
|   └── <REPO_2>    	
|	  ├── images  	
|	  └── instances	
└── ...
```

## 3.Multi-SWE-Bench report generation module

This is a module for generating reports on Multi-SWE-Bench datasets.

### Usage

```bash
python -m multi_swe_bench.harness.gen_report [arguments]
```

### Main parameters

- `-mode`: Run mode, optional:
  - `-dataset`: generate dataset and final report (default)
  - `-summary`: Generate final report only.
  - `-regen`: regenerate the report for each data only

- `--workdir`: path to the work directory where the results of the instance run are stored
- `--output_dir`: path to the output directory where generated reports and datasets are stored
- `--raw_dataset_files`: path to raw dataset files collected from github (glob mode supported)
- `--config`: Load configuration from json, toml or yaml files.

### Optional parameters

- `-specifics`: Specify specific items to be processed
- `-skips`: Specify items to skip.
- `-max_workers`: maximum number of worker threads (default: 8)

### Logging related parameters

- `--log_dir`: Path to the log directory.
- `--log_level`: log level (default: INFO)
- `--log_to_console`: Whether to output logs to the console (default: True)

### Example

```bash
python -m multi_swe_bench.harness.gen_report --config <your_config_file_path>
```

example_config:

```json
{
{
    "mode": "dataset",
    "workdir": "./tmp/workdir",
    "output_dir": "./tmp/dataset",
    "specifics": [],
    "skips": [],
    "raw_dataset_files": [
        "./tmp/raw_dataset/*.jsonl"
    ],
    "log_dir": "./tmp/logs",
    "log_level": "DEBUG"
}
}
```


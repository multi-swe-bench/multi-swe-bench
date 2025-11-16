# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-SWE-bench is a multilingual benchmark for evaluating LLMs in real-world code issue resolution. It spans 7 languages (Java, TypeScript, JavaScript, Go, Rust, C, and C++) with 1,632 high-quality instances. The repository provides tools for:

1. **Data Collection** - Crawling PRs and issues from GitHub repositories
2. **Dataset Construction** - Building evaluation instances with Docker environments
3. **Evaluation Harness** - Running patches against test suites in isolated containers
4. **Report Generation** - Analyzing and reporting evaluation results

## Development Commands

### Installation
```bash
# Standard installation
make install

# Development installation (includes ruff, typos, prettier)
make install-dev
```

### Code Quality
```bash
# Format code with ruff
make format

# Check formatting without changes
make check

# Run linter
make lint

# Auto-fix linting issues
make fix

# Clean Python cache files
make clean
```

### Running Evaluation
```bash
python -m multi_swe_bench.harness.run_evaluation --config /path/to/config.json
```

### Building Datasets
```bash
python -m multi_swe_bench.harness.build_dataset --config /path/to/config.json
```

### Collecting Data from GitHub
```bash
python -m multi_swe_bench.collect.get_pipeline \
    --out_dir <output_dir> \
    --org <organization> \
    --repo <repository> \
    --tokens <github_tokens>
```

## Architecture

### Core Modules

**`multi_swe_bench/harness/`** - Evaluation engine
- `run_evaluation.py` - Main evaluation harness; runs patches in Docker containers, compares against test suites
- `build_dataset.py` - Constructs dataset instances from raw PR data
- `image.py` - Docker image building and management
- `instance.py` - Individual test instance execution
- `pull_request.py` - PR data models and processing
- `gen_report.py` / `report.py` - Result analysis and reporting
- `repos/` - Language-specific repository configurations organized by org (e.g., `python/AgnostiqHQ/`, `java/apache/`)
  - Each org directory contains Python files defining repository-specific test configurations
  - Repository definitions are imported via `__init__.py` files at each language level

**`multi_swe_bench/collect/`** - Data collection pipeline
- `get_pipeline.py` - Main orchestrator for PR/issue collection
- `get_all_prs.py` - Fetches PRs from GitHub
- `filter_prs.py` - Filters valid PRs with associated issues
- `get_related_issues.py` - Collects linked issues
- `merge_prs_with_issues.py` - Combines PR and issue data
- `build_dataset.py` - Extracts test/fix patches from PRs

**`multi_swe_bench/utils/`** - Shared utilities
- `docker_util.py` - Docker container management helpers
- `git_util.py` - Git operations (cloning, checkout, patching)
- `session_util.py` - Docker session handling and execution
- `logger.py` - Logging configuration
- `env_to_dockerfile.py` - Converts environment specs to Dockerfiles

### Key Workflows

**Evaluation Mode**: Takes patch files and dataset files, builds Docker images for each instance, applies patches in containers, runs tests, generates `final_report.json` with resolved/unresolved instances.

**Dataset Building Mode**: Takes raw PR data from GitHub, extracts test and fix patches, builds Docker environments, validates instances, produces curated dataset files.

**Image-Only Mode**: Only builds Docker images without running instances (useful for pre-caching).

**Instance-Only Mode**: Runs instances assuming images already exist.

### Data Flow

1. Raw data collected from GitHub (PRs + Issues) → JSONL files
2. `build_dataset.py` processes raw data → extracts `test.patch` and `fix.patch` for each instance
3. `run_evaluation.py` takes model-generated patches → applies in Docker → compares test results
4. Results logged to `log_dir`, final summary in `final_report.json` at `output_dir`

### Configuration

Both `run_evaluation.py` and `build_dataset.py` accept JSON/TOML/YAML config files via `--config`. Key parameters:
- `mode`: Execution mode (evaluation/dataset/instance/instance_only/image)
- `workdir`: Scratch space for Docker build contexts
- `patch_files` / `dataset_files`: Input data (supports glob patterns)
- `output_dir`: Final results location
- `repo_dir`: Local repository clones
- `max_workers*`: Parallelism controls for image building and instance execution
- `force_build`: Rebuild Docker images even if they exist
- `specifics` / `skips`: Filter specific PR IDs to run/exclude

### Repository Structure Pattern

The `repos/` directory uses a hierarchical organization:
- Language level (e.g., `python/`, `java/`)
- Organization level (e.g., `apache/`, `google/`)
- Repository-specific Python modules defining test configurations

Each repository module typically inherits from `PullRequest` or `Repository` base classes and customizes:
- Docker base images
- Environment setup commands
- Test execution commands
- Patch application strategies

## Python Requirements

- Python >= 3.10
- Core dependencies: docker, gitpython, dataclasses_json, unidiff, PyGithub, swe-rex
- Dev dependencies: ruff, typos, prettier

## Docker Usage

All evaluations run in Docker containers for reproducibility. Images can be pre-downloaded via:
```bash
bash scripts/download_images.sh scripts/images_mini.txt
bash scripts/download_images.sh scripts/images_verified.txt
bash scripts/download_images.sh scripts/images_rl.txt
```

If images don't exist locally, they will be built during evaluation using specs from `repos/` configurations.

## Testing & Validation

The `syntax_check.py` script validates repository configurations for consistency (checks for incomplete `__init__.py` imports and orphaned files).

## Multi-SWE-RL Community

The project includes a community contribution system for building RL datasets. Contributors can add new instances following the workflow in `docs/contribution-demo.md` and `docs/build-dataset-quick-start.md`.

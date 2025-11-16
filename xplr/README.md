# xplr mini-swe-agent Workflow

Everything in `xplr/` exists to prove that Multi-SWE-bench can drive the `mini-swe-agent` repo end-to-end. Keep it lightweight: one script builds the environment, one script runs the workflow test, and one JSON file captures the output.

## Setup & Test (manual steps)

```bash
cd /path/to/multi-swe-bench      # repository root
uv venv                         # python -m venv .venv also works
source .venv/bin/activate
uv pip install -e .              # install multi-swe-bench dependencies
python xplr/test_msb_workflow.py # run the integration test
```

`test_msb_workflow.py` prints a six-test summary and writes `xplr/test_workflow_config.json` so you can inspect the generated instance metadata. Use `bash xplr/setup.sh` if you prefer a single automated command; it just wraps the steps above and re-runs the test.

## Autonomous mini-swe-agent workflow

The repository now ships with a turnkey script that collects real PR data from `SWE-agent/mini-swe-agent`, generates a `raw_dataset.jsonl`, and runs the Multi-SWE-bench dataset builder. Everything (raw inputs, config, logs, outputs) lands in `xplr/artifacts/`.

```bash
# Optional: override the PR numbers that get processed (defaults to 1)
export MSA_PRS="1 2 3"

# Run the end-to-end workflow (saves intermediate files under xplr/artifacts)
bash xplr/run_mini_swe_agent_workflow.sh
```

The script performs:

1. `xplr/scripts/prepare_mini_swe_agent_dataset.py` – hits the GitHub REST API (no token required, but it honors `GITHUB_TOKEN` if set) and writes `xplr/artifacts/raw/SWE-agent__mini-swe-agent_raw_dataset.jsonl` plus raw `.patch` files per PR.
2. Generates `xplr/artifacts/config/mini_swe_agent.json` that points the builder to the local artifacts folder.
3. Runs `python -m multi_swe_bench.harness.build_dataset --config ...` with logs streamed to `xplr/artifacts/logs/build_dataset.log`, and final SWE-bench-like instances dropped into `xplr/artifacts/output/`.

You can re-run the workflow at any time; the script always overwrites the artifacts for reproducibility.

## What you should see

```
✓ PASS  Instance Registration
✓ PASS  Dockerfile Generation
✓ PASS  Command Generation
✓ PASS  Log Parsing
✓ PASS  Files Generation
✓ PASS  Configuration Export
Results: 6/6 tests passed (100%)
```

If something fails, re-create the venv (`rm -rf .venv && uv venv`) or reinstall in editable mode (`uv pip install -e .`).

## Files that matter

| File | Purpose |
| --- | --- |
| `test_msb_workflow.py` | Pure-Python smoke test that exercises the Instance/Image contract without touching Docker.|
| `setup.sh` | Convenience wrapper that ensures uv exists, creates the venv, installs deps, and runs the smoke test.|
| `run_mini_swe_agent_workflow.sh` | Fully automated data→dataset workflow; saves everything to `xplr/artifacts/`.|
| `scripts/prepare_mini_swe_agent_dataset.py` | Helper used by the workflow to fetch PR metadata and raw patches.|
| `artifacts/` | Directory where raw data, configs, logs, repos, and datasets are written (gitignored).|
| `test_workflow_config.json` | Artifact emitted by the smoke test so you can copy config snippets into other tooling.|

Everything else in the repo belongs to Multi-SWE-bench itself.

## Customizing for another repo

1. Update `create_test_pr()` in `test_msb_workflow.py` with the org/repo/PR you care about.
2. Adjust `TestMiniSWEAgentImage` (base image, scripts) and `TestMiniSWEAgentInstance` (parse_log, run commands) to match the project.
3. Run the test again; once all six checks pass you have a new ready-to-use Instance template.

## Troubleshooting

- `ModuleNotFoundError: multi_swe_bench`: make sure you ran `uv pip install -e .` (or `pip install -e .`) inside the venv.
- `uv: command not found`: install it via `curl -LsSf https://astral.sh/uv/install.sh | sh` or just swap the commands above for `python -m venv` + `pip`.
- To inspect the generated configuration, open `xplr/test_workflow_config.json` after any run.

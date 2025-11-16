#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
XPLR_DIR="$ROOT_DIR/xplr"
ARTIFACTS="$XPLR_DIR/artifacts"
RAW_DIR="$ARTIFACTS/raw"
PATCH_DIR="$RAW_DIR/patches"
CONFIG_DIR="$ARTIFACTS/config"
WORKDIR="$ARTIFACTS/workdir"
OUTPUT_DIR="$ARTIFACTS/output"
LOG_DIR="$ARTIFACTS/logs"
REPO_DIR="$ARTIFACTS/repos"
CONFIG_PATH="$CONFIG_DIR/mini_swe_agent.json"
DATASET_PATH="$RAW_DIR/SWE-agent__mini-swe-agent_raw_dataset.jsonl"

mkdir -p "$PATCH_DIR" "$CONFIG_DIR" "$WORKDIR" "$OUTPUT_DIR" "$LOG_DIR" "$REPO_DIR"

PR_VALUES=${MSA_PRS:-1}
read -ra PR_LIST <<< "$PR_VALUES"

echo "[1/3] Fetching mini-swe-agent PR metadata (${PR_LIST[*]})"
python "$XPLR_DIR/scripts/prepare_mini_swe_agent_dataset.py" \
    --prs "${PR_LIST[@]}" \
    --output "$DATASET_PATH" \
    --patch-dir "$PATCH_DIR"

cat > "$CONFIG_PATH" <<JSON
{
  "mode": "dataset",
  "workdir": "$WORKDIR",
  "raw_dataset_files": ["$DATASET_PATH"],
  "output_dir": "$OUTPUT_DIR",
  "repo_dir": "$REPO_DIR",
  "need_clone": true,
  "force_build": true,
  "specifics": [],
  "skips": [],
  "global_env": [],
  "clear_env": true,
  "stop_on_error": true,
  "max_workers": 1,
  "max_workers_build_image": 1,
  "max_workers_run_instance": 1,
  "log_dir": "$LOG_DIR",
  "log_level": "INFO"
}
JSON

echo "[2/3] Configured build at $CONFIG_PATH"
echo "[3/3] Running multi_swe_bench.harness.build_dataset"
python -m multi_swe_bench.harness.build_dataset --config "$CONFIG_PATH" | tee "$LOG_DIR/build_dataset.log"

echo "Workflow complete. Outputs are in $ARTIFACTS"

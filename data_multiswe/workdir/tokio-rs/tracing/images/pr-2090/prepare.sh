#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 465f10adc1b744c2e7446ebe2a6f49d5f408df0f
bash /home/check_git_changes.sh

cargo test || true


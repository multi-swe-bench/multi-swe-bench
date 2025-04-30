#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d5cf64d6a8c4d5911008ce4af6b41caeca6e8bf
bash /home/check_git_changes.sh

cargo test || true


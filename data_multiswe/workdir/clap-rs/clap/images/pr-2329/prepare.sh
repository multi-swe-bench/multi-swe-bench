#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b59f5d3699134190d8d5f7fb052418edfd4999f
bash /home/check_git_changes.sh

cargo test || true


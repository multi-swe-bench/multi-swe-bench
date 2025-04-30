#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 7d3a380b3da9b32873ea2dfaf54fd673c6f39e28
bash /home/check_git_changes.sh

cargo test || true


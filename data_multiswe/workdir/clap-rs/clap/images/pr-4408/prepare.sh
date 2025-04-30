#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 996636d56f69f3591e88cdc3c3c346352fa3653a
bash /home/check_git_changes.sh

cargo test || true


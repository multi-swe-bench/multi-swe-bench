#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e3577f6f3995b92accee21e0737c25ef0f1953c
bash /home/check_git_changes.sh

cargo test || true


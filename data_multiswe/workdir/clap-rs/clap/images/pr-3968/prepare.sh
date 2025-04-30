#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a4da7e777a0acf442b491500cc8c7bfa78f6eac
bash /home/check_git_changes.sh

cargo test || true


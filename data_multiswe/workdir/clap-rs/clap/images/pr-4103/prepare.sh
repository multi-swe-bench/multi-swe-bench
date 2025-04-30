#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout fefeb7ee6fc1c90f760fb27b4d5daf773973b0ce
bash /home/check_git_changes.sh

cargo test || true


#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 63015eb8d9c5261d9a384e11dc84552f23a5209c
bash /home/check_git_changes.sh

cargo test || true


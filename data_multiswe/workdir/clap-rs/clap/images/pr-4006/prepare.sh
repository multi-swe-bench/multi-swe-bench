#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout b2a8fd7f46a7480512d5af8157041f5ce4c2c2b7
bash /home/check_git_changes.sh

cargo test || true


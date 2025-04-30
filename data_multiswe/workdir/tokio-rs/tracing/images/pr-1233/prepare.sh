#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 881091a1dd5d3126faeabbca9e3779f1d16c3cce
bash /home/check_git_changes.sh

cargo test || true


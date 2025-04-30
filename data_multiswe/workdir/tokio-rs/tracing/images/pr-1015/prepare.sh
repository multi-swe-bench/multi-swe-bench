#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 0dc8ef2da97f605689fff17f6c38b69e105a5281
bash /home/check_git_changes.sh

cargo test || true


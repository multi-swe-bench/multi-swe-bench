#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 3c3f59e68f1771dabeb020c0aa0f30b8c9c59936
bash /home/check_git_changes.sh


#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 79602f9ecd9559954f844774a90286305b13e056
bash /home/check_git_changes.sh

pnpm install || true


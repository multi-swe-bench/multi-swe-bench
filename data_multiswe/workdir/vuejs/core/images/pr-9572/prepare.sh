#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout f6babf32363185ff3ab3512d952a8a9aa9603762
bash /home/check_git_changes.sh

pnpm install || true


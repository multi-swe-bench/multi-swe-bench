#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 3f92126a26a544dfa69211cf2977556a2706bb2c
bash /home/check_git_changes.sh

pnpm install || true


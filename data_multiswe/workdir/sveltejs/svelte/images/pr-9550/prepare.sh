#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9926347ad9dbdd0f3324d5538e25dcb7f5e442f8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


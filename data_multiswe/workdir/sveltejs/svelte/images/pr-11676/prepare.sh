#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1784026843d2f7de6e449a5587da5dc30d467818
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0d5a32d5f7448363e767c49a68ba5c1a3a5dc262
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


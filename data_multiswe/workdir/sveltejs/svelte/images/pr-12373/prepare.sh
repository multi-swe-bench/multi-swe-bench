#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4e8d1c8c52a4b1aaa10bbf79aa02e0d44df63e50
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


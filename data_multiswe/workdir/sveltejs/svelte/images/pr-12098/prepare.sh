#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 97e5b5285adf05933bdc5cb047cf9df0db832a2e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


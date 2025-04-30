#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a212b0d2fe149c3c57faa0520d461c59a9d45f67
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


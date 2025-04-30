#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 90d6f573e316f86f6a998d73b3cba1b03a5d15dc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


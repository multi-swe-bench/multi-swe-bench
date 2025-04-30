#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 551284ca2259d934d34b71a38071d85684bd6d4f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8148e63ced607f13bf4f5e4a88ee90d91200b2f5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 405e9da4ff853c2e8aafde739ba0b2fd406f56b5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


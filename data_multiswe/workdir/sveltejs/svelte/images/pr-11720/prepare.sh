#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0128df33da19c0839eaab2f1da7525125dcb1ac1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


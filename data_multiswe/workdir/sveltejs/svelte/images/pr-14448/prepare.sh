#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a8aab0e384c5706a9cf34aba69f56b050b1e549
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


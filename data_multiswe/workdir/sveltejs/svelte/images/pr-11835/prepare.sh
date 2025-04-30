#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 22e2aeca76b3049c2b249712885a98d148d74c4a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b0bd8b23a0c6e81446d0700031621c9dc448bb3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


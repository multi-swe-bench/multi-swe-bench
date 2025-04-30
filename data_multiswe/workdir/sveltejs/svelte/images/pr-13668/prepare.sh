#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 969e6aa750a4dccf3566fd4b12545f83e2492c72
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


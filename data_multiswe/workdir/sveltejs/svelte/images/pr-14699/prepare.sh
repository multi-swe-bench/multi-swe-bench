#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 61a0da8a5fdf5ac86431ceadfae0f54d38dc9a66
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


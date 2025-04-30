#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9a887f8dab8e4846bff8734cba982bcdae44d401
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


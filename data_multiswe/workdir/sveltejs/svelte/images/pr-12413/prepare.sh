#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b160786a7370df3e332be703c55327d38a061b7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


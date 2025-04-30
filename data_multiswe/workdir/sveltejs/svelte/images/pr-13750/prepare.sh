#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 28c8d2b95dcd8b8098dbdf4b28c9ff5fc815ddff
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


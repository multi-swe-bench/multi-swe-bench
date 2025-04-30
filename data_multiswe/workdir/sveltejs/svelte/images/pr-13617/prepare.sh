#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 76067a5fbcf15143b0c0f9d60234f4560d0966c7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


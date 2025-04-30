#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0f4f3d7df04cf749e3fe35fc9b625fdc7b61dc9c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


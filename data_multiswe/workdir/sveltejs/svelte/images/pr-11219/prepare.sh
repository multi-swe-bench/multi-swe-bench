#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 70b47de124e779f3daa4db5f43431051b5f936d0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


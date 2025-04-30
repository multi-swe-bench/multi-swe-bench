#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ae3d472cbc7c4b6f5ae461ea40146b44d77f7738
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


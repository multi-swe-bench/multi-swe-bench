#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 312dd51acc44d92ab855f7eaf15d2d9150c0a6f3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


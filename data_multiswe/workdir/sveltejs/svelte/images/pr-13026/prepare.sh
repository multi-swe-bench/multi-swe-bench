#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout bc1624ffc83bbbf480d449a54b6e9b04c0a7c521
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout fff3320517baf94abef277ce01f2104526d1a0e4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


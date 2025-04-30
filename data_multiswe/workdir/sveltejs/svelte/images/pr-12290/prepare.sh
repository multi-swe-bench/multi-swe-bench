#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2f1d2d5906771a2879f6f77fb62f59bc0b31292c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


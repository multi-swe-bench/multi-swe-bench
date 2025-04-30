#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 189113ab8e33f4df548717ea508249881e1d760e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


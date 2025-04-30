#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f0dde52077478349762f4c7ba53568905426420
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 72f5539f5161797c868f191b73fed9784ad671d8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


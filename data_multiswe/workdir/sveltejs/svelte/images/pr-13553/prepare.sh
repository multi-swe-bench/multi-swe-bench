#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6776947ae85e58a2a947d1ce3143b4af3f799466
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


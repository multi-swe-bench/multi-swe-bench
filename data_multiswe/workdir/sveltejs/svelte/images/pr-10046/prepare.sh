#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6307a3322c2087286e8013a9aa2e6911e9a36d01
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


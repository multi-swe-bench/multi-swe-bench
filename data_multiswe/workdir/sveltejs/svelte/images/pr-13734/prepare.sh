#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 41b5cd6f5daae3970a9927e062f42b6b62440d16
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


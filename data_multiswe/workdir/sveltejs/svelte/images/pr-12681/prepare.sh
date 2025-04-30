#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9411b6f9f1c6c78362ca97643063955a7256c296
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


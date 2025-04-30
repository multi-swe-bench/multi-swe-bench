#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout fd4a52c8944b9e131594d6fc0e00645f12215304
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4aadb34c02dc6afce56bb0f66bbac117ac56c4e8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


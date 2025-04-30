#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 434a58711f7ebb2c3849545542b4394d295ccea9
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 84ad208f2e986fa549683a12e7f999c3d31b127f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


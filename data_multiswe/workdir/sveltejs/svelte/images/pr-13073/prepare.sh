#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b8801cbbacba9fe477c312b92e0f2ae29909547
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


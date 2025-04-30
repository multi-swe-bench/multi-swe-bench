#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 501f4151909077020f26135a90425bf175b03c1d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c5c54dabcc7e93e59b1354911faca8961351f2ab
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


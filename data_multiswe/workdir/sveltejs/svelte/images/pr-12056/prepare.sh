#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c3da6a491f401998e8b64b8fd330fa63bff00e10
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


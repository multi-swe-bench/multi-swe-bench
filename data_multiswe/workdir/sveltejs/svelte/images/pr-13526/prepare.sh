#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout db305a07f25ad7370e7ee96f5d3d73ba575ea712
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


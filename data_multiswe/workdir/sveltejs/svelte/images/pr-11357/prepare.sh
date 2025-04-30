#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout bda32edb1a4f2d383d96071750d6bfa9421b2175
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


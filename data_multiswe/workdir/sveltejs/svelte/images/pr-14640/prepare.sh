#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ef8bd6adeb238f2d8ccc8c04547e9e16cb932c25
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


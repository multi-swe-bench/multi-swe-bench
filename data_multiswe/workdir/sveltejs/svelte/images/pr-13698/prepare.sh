#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0fdfd9c50cbc236d80995721176237243ca11ff4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


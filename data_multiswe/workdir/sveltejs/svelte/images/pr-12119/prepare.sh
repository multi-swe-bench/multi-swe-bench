#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 7295facb6c9b754a9d4e1b3abf6eab5d3263148a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


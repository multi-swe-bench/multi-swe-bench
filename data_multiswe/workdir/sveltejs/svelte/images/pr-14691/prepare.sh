#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ba1b9ddd0bc65b9a790030aa8b7c73ae2990543
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


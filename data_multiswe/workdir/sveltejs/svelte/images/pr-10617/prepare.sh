#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 86b3ea8c23a17af9af9ffb156565fcd5e0fe81fd
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


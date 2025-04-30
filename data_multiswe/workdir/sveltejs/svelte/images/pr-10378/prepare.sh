#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 89123a81176075da4561b4045be65a1cc2f39ecc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


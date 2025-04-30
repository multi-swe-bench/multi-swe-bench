#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 47918328d7dacec0663c8f9a121a1dffc190c59d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


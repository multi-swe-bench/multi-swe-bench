#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 88582479f2d4bae08d055585a4ef2256e599e107
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


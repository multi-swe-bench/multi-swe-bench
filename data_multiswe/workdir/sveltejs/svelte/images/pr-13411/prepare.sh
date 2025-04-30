#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 276443fe5e9d139cf89e18370367e97125b39a82
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


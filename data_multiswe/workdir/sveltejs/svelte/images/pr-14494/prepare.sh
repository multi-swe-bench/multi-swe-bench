#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 99b4cfbb510af722d3d111dac4d0059766ba6610
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


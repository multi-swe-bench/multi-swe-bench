#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 91299b32ff4edf451cd3d912b208338dbfd117dd
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


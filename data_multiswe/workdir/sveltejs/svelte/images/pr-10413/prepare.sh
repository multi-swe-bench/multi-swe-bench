#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 268ac95fde573dc26e96dbd3e581c01611a55de7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


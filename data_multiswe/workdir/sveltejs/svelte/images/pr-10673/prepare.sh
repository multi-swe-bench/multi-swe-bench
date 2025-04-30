#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1ac313594c28d729b7e11aedc1822fd8e40bd610
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


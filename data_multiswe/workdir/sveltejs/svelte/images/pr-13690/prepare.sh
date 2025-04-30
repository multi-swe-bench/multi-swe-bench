#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout fb052be96e6c2a38a74f3f595072f38128744c48
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b3c002a703f5da810620b84d67b7ccabe23027cc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


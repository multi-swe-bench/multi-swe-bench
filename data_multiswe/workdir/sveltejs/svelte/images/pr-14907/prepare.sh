#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ed26c3f658acb0292f06e6a437d42bb64e804447
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


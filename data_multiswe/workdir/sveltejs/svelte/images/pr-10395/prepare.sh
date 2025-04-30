#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 97d3ec2f89897f2f17126734016a6adb56c95e49
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


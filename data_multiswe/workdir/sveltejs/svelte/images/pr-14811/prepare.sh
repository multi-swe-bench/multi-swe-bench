#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 32348a5387ed8607e4bd688eddd3aa87c17abc21
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


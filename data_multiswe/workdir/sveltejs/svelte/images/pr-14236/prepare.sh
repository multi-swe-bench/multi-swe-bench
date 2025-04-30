#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4bcd01b9941c7ba393738b5e038d9f4ad96b3bbd
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6acf7f3fc3609c28395c77d7953a66509c857db5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


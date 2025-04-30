#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 37f249350c414d9a75635bf2993b08f888191ce5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


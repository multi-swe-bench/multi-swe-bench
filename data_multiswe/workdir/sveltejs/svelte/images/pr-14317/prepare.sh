#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout efc65d4e0c185cd597a6eeef013f6641b8e25d50
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


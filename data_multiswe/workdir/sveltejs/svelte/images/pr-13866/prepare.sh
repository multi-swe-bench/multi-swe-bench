#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 60dcffb8564bfcc1401ae4c934c742e31a24bc2f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


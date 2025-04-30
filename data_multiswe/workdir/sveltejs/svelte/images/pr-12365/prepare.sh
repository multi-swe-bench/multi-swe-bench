#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6ac1ae8a12552f8a4444f3b1bc938d2989c7726a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


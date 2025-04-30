#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ef640c3b461783aef983d091712b7e9271d2cc4d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


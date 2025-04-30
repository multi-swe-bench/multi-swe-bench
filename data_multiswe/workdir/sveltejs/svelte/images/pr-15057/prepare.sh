#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout eee808fb79cfb182df7285b7107d5f7d2bee44d1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


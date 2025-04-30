#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout dc8ca4661f10fe703bb7aa700abc6287cd5a8cdc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


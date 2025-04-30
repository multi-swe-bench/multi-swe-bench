#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 30b143cef0d5ea17a6edec33496681882eadce34
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


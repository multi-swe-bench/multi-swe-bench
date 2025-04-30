#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 33ee958087d5110ee4aee4b1f1cb30c7ac30a186
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c66bf178aae18c2b4d8ac189a48cf10c47e4d417
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1d3c4397b2f7fe01b3e5983e647f5a27dd63e67c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


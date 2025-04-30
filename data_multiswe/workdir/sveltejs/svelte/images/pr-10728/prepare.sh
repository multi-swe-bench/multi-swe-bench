#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ae4af6841aaeb7b580ca5be2454318a3bfdaa05b
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


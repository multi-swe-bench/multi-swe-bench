#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b802dbed328178263aaf2f1e967655f53be2399
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


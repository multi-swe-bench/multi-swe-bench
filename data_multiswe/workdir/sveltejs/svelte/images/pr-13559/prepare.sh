#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d220edd75439fde00a60145b78ba7cc6d707f210
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


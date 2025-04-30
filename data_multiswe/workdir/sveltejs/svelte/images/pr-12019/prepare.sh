#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4cdc3710d02e2c968801995113e6604cfdd5db29
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


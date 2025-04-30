#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2b7e109f61c8588fd0b0f4783cfdb2911d67083d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


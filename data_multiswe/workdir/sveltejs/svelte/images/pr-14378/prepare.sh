#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d12fd1a01d7020855122a8bfb5a35a3dd4e1c8f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


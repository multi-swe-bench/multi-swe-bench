#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3624a4c2a00cda7e18ddf6331015995dabd30932
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


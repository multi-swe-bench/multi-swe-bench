#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b665425e5d2e41c11b3f3fd56e78b515709401c4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


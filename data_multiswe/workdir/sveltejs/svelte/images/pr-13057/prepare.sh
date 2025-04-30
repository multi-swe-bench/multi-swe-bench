#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a1d1012e9dcc87ada9b8a80796f8db7e5fcc77a3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


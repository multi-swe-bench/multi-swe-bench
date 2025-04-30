#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8578857332c27005866661a22734b1bf2d83b69f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


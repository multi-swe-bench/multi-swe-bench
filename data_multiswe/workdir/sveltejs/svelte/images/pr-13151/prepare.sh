#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b88b88886bdf8fef064140e91938e162e80813d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


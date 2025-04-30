#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a65e68ca37d171663feec99382efd46e7cea364f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


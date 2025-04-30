#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout f5102013af6ba14774c0fe2d575ea8e06b92697a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


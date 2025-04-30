#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d93ad3ba1e8c28c2facaec49e19d2ac1ed577e9f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


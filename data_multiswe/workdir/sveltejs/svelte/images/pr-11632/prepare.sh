#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f8bba2f802dd99888d83909abbc336cd7127f80
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9f51760dc64a16b047bf43372d7544471dd2d92d
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


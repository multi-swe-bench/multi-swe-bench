#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 5797bb34ce96b0d7b4608f934c1f13605143671f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


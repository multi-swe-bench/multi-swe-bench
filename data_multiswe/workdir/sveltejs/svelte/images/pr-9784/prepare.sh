#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 10aacfa603d7a7f139ca3c63556c2ef7af071ba1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 436cc997406b3cbac3c1f84efb81d6b1d81befd0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


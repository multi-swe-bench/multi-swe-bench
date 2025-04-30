#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 092370b43fcb1b76f1c4cf713d1806b8ecb4932b
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


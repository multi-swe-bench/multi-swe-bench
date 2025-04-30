#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f855e627f0e5321855cd4b61ad0822368e1c545
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


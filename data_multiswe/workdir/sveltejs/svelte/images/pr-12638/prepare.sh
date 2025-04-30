#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3bff87ac66251c60a92cf244d54aeb8ad8ece5d6
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


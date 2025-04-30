#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8b1a26904a0d50d058564198904db578276ae775
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


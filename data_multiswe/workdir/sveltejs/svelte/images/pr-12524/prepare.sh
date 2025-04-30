#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0891fa7a18fb2303cc60791a3b5e6739c78fa5b4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


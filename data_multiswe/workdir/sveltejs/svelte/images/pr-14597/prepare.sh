#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 08e2cf25b03707f4ca6e44a1e6ca0480190c14a1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


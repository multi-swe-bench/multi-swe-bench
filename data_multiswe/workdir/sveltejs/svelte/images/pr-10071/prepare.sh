#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2133d7d67afc9908b9b7803bf76a0e2755ff913a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


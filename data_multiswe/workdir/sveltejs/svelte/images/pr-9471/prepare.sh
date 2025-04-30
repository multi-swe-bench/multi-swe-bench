#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 73e8820fe724cad5fd7ea3cd5b3faa652f04064e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


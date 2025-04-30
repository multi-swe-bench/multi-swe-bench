#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ea22840e8c0537388e9839ad337d1aa6f0bd90c8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


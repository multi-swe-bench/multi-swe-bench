#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 7ecc6c076ca5aa5174882abd80837a1fcc0b1cad
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


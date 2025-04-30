#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0332abbd83f3edd2831c1ca8c2b19ff2aa22da60
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


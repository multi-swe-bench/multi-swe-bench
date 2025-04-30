#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 5eff68f63df8fd2ccc3b0e591e47a43da4f8ccb3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


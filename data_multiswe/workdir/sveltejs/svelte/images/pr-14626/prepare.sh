#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c1c59e77a54109e6dd868e8ee7884caf9a275f5a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


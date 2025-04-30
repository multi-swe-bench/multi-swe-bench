#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4e61db7201c5320c6cf0bb323fa82659c56c2f37
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


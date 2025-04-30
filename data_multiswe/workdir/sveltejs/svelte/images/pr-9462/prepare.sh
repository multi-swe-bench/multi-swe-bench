#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout f5101c0d8cb34cd488af0b56784fb308541d62da
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


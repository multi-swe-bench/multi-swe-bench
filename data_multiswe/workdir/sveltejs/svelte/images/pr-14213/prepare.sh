#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ea0d80e1950b5c62547c69a26c823282e8d88ad3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


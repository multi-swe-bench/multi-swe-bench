#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1d8d38c8bdfe66571299805a00ea69cd0e8c8ac5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 256e60994e8d4745f9444b0ce372490b7c01800f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6d65b2f8ad68365ae3f24be36f718c09eeb591da
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


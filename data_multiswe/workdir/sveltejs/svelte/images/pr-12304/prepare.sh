#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout bc32b7c8289fbba4ddc1ea436cfc42eaf3ce1f68
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


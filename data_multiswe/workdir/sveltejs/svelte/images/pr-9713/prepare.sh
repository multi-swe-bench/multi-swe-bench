#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout bde42d56764337e000ca72df921fb2d168067af1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


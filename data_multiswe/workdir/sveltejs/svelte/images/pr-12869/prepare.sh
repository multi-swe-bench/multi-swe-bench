#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e4b7304365d5f0c95223bcaa25290f933174d40e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


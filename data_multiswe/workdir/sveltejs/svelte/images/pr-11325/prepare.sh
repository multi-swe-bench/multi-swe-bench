#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e17428316cbad94d21306b75f6ef4d389b6e301
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


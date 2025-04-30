#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout cf6b64c6c0220068abb2843fea78b125b8767f44
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


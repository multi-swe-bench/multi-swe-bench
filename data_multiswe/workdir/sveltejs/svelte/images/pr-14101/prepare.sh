#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e7d68d8c10d4864cb4c58cd86f6076c187b22ec0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


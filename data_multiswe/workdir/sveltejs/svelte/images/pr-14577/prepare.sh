#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 60c0dc7a2dd1cef1f71c5a9176e52bf8a001d5e0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


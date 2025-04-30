#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a0b822f4826b82454962a94c072519530b7c126
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


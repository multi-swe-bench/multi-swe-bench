#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 570884eabda10a28e640ae3fdeae64c2f1a587b8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


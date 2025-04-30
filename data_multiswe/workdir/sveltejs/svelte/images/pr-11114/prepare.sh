#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a531625896b5b05cebc21114bf2a03f6a619594b
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


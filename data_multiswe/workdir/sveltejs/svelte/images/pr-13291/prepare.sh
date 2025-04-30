#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 758fb2aa0fe6f12fcf7da384613fea183249f66c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


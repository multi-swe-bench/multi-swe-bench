#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ede1edd314452a1bfd729503e990cf06e04da641
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


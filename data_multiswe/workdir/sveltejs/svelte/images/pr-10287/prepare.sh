#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 340934917a2bb8c0395934bf0c472bd3e067edb7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


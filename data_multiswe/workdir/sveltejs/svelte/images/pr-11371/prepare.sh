#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c7bdef595b7673c952ec4c6d3b7bee0916eb477c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


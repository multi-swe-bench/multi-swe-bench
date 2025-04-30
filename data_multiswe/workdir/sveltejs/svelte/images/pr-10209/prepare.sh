#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1798e58300235e1ee318b1dd4f6601851ecef5b0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


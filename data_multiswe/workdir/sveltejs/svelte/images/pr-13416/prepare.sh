#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 35ebbe61adfb09a780806d70f5c0067e6ebd78f7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d4718e0755eac1e505292d0fb7cfd8682eca3048
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


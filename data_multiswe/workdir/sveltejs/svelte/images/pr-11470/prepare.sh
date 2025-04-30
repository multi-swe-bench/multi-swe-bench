#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout f2f71ae3a1b9a416936484c121e51f6645761ea8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


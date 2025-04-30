#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout eb3e677e05e581be60564bbbb6bf9ff96727d22c
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


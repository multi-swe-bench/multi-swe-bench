#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ae7d73453ca388561ecdbdcae0cccd1cd335f954
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


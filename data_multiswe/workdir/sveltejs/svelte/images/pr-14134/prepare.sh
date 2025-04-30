#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a952860232203cbb3228387f5a3e70de28192796
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e8ce41815a734b296aac0f03d9df99abea209c8a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


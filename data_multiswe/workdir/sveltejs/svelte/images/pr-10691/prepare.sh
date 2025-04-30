#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ee04f973b29367769b702e3b60b34191a1f24ac5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


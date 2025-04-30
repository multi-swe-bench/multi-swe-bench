#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f99935b992f0db255fd8d93138af00398e4b56f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


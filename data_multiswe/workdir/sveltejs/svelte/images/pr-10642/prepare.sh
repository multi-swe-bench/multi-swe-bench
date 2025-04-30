#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a4a789db4dbd43c6fc39de93b4d610ae85a63423
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


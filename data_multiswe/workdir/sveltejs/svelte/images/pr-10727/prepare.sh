#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3fd02f1c49fd43f59b27dbd4822f351693a63301
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


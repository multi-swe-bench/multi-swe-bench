#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b91a67ba6845c5d37dbb6f2fda8a0d057f828dab
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


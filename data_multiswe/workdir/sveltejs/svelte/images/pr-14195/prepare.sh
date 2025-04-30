#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 44a833fafee1dc760dfc6f18f2e699b74cb4baea
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


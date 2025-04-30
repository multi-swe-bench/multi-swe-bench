#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 77ed790fb3a6d0af3e6470ba660fc0e91a836f2e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 879b0119d53e93c118c9c8519f0f7f54138c34d2
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


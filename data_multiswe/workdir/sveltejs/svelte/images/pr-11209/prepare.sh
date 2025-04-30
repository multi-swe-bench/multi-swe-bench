#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d51075c154beed08ec706172bfab51cbaef5ec2e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


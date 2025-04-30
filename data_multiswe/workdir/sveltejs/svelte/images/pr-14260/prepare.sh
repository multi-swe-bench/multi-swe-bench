#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ae9f53a3bde79e8777e865acac3b99612c2cec71
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


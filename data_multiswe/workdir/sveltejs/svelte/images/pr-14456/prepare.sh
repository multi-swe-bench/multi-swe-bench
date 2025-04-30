#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e9ff665bead20d84df4464526a026b2070f3278a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 36ece1c38114a7d1b4177829f76201eaeef7a6f4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


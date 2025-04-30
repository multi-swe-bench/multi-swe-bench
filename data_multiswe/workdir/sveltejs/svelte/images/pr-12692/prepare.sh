#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4aa815f1ec13722f4f0fbc1a0dcbe707fa476294
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


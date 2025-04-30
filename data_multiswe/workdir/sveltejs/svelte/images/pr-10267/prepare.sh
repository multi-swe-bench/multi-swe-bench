#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 036e88f1f76e50f40807f12cb8309fa2c0837c60
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


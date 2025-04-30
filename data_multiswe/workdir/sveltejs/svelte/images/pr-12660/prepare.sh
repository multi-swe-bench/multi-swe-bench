#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d20e0646745cbc9d835b05b65077146105bc4130
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 019b26b775038f2df22a7e853447ce14e2b1ede9
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2fa06447cf51893715bfe776f753d1b1f0587d83
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


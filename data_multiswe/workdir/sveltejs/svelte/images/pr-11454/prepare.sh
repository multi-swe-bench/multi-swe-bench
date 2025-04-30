#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2ebb277be70e9333a24f20bae01be2383b434e0e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


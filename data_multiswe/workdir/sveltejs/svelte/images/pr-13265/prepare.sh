#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d9369d8e309640f71d7a8559dab8c5fb0ee982e4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


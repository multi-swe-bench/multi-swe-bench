#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e8f7437cf6d5d95811bfe472209826e4c6fcbc31
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


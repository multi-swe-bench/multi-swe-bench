#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6655f2c5d2d873f0bed4bf45220d185bb8a189a8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


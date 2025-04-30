#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 357e1a74b4af25c3e3839d303cc3d8d239d43087
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


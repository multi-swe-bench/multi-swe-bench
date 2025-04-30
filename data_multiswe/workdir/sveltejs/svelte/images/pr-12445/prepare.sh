#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a8dc96eb4345c51efd1e5f0cc02781b18aba322a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


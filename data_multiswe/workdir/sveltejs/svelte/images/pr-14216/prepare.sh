#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 53af138d588f77bb8f4f10f9ad15fd4f798b50ef
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


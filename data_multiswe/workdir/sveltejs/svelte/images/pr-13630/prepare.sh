#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout f579a3ba7d8f088d1d4f8625758e5e5598c9ebfa
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


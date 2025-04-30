#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3d67cd53dbee6079834e208de4f65861798a3131
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


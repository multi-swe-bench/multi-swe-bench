#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c287bd503d5b73af1b3aff9ef210341bfcddc642
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 388e3e68fc46fd018e58a82572d45f704e6e9c8f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ca6e9b5745e80b544c404bb74a968b68aea59c40
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


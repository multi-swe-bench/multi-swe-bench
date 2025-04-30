#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6534f507ce0a39b50b851d67868a1716cca6efae
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


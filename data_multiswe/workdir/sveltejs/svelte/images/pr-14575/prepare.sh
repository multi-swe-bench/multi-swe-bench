#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a6b4ec36a11bb4434311c4735ff846b79c00ba0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


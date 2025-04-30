#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 32808ac054a83f294024b57aa0bde3cbb03b86d6
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


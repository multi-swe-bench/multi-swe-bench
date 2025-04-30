#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 48e620515dbb79ca8caf39634f2fb601d6a8534b
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


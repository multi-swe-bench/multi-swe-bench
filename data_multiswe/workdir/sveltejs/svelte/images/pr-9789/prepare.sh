#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 24777c335a85209e344fb2b61a60c7768165c747
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


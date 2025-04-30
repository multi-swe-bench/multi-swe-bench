#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4ef64541dd09eb065eca44df6ef3dd3c3aedfbfd
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


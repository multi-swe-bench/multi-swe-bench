#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 34079a0ec57693cb419cf8ebffdb64f3ce69f24e
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


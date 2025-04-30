#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout eb6488cd905c1d5bc9a88bed4e1716cbb88fd14a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


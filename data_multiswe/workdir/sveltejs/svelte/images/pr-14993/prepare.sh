#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8a1acac084096d9c9bd15a1356d3251383e8d258
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


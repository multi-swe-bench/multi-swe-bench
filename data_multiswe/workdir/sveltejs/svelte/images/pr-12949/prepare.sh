#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout af35fb7ae6be1d4b4dea00c7e49379e7bbd7d3c6
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


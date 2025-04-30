#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a1f371e78656f951ad75945493a798716ecc92c4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d509de2503f5049edb19e9f8e9b3a09182ebaf92
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 77b1f2fe516f699bf916697db8805a7d3b259c37
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


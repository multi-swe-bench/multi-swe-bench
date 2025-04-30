#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2861ad66e054d2b14f382aaada4512e3e5d56db8
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


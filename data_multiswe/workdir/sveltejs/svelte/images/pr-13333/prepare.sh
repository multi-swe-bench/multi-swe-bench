#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e4926d7507e128d2b13e2936131c10133fdbd920
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9abfb52f67bbcdc7b671c3b3dfc3d672c506a24a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


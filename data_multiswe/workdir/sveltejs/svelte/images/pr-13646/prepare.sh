#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 372884cf99420dd9d343a4ad78f6aa540a4df289
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


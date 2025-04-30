#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b0374f8863538c7ae9d035c00c824b7c043bb4e0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


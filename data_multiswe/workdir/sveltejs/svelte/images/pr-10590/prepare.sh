#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 58008479fc8478edebdc6e343738b856bb50d8a9
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


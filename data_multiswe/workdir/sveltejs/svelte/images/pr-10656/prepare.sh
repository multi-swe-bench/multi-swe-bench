#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3fe4940a9da82b8e95db7074c0d6171c685fc911
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


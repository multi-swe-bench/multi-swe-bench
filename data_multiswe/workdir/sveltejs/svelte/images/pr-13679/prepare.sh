#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 894b1c37ad524dca9d2527fc761d56b478b7dd7a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


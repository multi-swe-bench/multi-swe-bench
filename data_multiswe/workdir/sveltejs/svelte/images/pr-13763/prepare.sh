#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 41d61c7a375bb193547e3044dbbf8f78a201e871
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


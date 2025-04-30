#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout db0b802fc2a8d0cd75f3dc209f19e06712be5a92
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


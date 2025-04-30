#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4a0c90e87de3bf1b1d74f287049bc018565d65e1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


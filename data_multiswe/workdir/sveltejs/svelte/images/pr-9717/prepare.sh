#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e3dc185a4c3420788ea50863dda50c7820bf6ae4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


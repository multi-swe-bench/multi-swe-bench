#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a764f4e88ead69f71565da58eb5eab5c6de16a2a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


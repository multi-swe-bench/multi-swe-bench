#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout a8ca2a490407581cda3fe3dc9a1e0588132ba44b
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


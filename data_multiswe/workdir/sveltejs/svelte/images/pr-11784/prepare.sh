#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d1f5d5d33d228106236089d062d27c7d4696c930
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


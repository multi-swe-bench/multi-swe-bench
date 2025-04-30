#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 2efae794b893d4b852cfd0a1ad656f2d6ad83d03
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c5fa0b46e1b74bce71332e08636d4f74496efc43
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


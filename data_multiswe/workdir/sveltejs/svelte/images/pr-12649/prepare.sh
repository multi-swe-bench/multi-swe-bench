#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e417d3a2d281a5ec9b595be5ffbd47efe57b28c3
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


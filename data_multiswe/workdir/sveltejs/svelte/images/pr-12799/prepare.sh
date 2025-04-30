#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 09db33979d17d176c6b48370e8006e293d577074
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


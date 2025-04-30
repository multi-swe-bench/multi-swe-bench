#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 09510c8c5c0888578446781e54f2229428e21bfc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


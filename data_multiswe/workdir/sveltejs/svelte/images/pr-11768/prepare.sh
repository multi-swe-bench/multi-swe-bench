#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d856c500924cc620f60ee32047df3c4620c3a5ce
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


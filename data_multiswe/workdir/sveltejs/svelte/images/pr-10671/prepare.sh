#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b1b51a404b1357558e963716c6182ecaccd24f20
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


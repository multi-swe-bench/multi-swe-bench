#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d87bf178c51c1edea94eeb854cef2bf05bd02688
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


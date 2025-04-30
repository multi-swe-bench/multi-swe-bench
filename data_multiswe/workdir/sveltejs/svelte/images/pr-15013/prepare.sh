#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout dfa97a5e643655d919a7c6ff80fb3841fe1111f9
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


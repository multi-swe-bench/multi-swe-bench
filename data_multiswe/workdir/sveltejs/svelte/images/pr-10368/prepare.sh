#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b78c14be88ef33bf0ea2922c50e331fdf217d56
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


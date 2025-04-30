#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 053159bf0b5679e3b9bf2c4c2710fb92d810221f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


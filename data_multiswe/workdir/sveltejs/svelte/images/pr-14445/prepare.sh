#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout f2eed15c021b038a77cb97e71c565823ef2c16fb
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


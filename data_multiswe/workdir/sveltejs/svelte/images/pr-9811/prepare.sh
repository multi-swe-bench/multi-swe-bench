#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d5167e75b96e10f0ed8f9b84588079d66dffaec6
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 95d07de7f9711855295c3b0ce8adcada10981b12
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


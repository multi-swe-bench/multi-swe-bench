#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 1108587f1bb65b816ff692161fec1599e7f99c47
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


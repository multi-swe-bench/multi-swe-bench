#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 4c4f18b24c644f7e17cd9fea7fde777f3324e206
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


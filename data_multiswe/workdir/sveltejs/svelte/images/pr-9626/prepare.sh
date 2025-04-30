#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ef68b66dee1ebc126118e5b837c091e110999c81
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


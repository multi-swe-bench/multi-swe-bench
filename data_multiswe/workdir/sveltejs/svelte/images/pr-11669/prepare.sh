#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c70533a5a753c9478991812e647e5bcb9dcb19a7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


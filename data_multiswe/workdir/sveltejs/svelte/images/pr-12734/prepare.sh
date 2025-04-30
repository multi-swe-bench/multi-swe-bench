#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e66416bec779ba4fba58c1bc670e119052489baf
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


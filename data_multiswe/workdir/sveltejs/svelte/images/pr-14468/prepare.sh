#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c4ac0e01e75eb20e99f6a31e974c6bc5b5f00dc7
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


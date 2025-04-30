#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b3842d79823ba713fd150c64f8896d4b3f03a00f
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


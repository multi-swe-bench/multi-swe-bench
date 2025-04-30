#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout cd798077b464ab3a28227f1e4a9aace20ba29b28
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


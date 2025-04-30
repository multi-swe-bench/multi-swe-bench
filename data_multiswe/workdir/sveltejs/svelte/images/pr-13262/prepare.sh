#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6ed45db20fdec3d43e833851281203af7b599533
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


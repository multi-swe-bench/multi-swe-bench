#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 3f6eff55a4dc6d6a76efb2f23a971f15ee524ddd
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


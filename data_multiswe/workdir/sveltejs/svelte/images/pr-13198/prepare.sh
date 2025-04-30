#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 25f67df91117b649766144d6ec23425901877083
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


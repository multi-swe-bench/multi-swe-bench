#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 68071f7c0658e72c2dc0b8cd0bb81a4bd39127f0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


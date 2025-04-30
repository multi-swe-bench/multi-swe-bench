#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 9666215e6d975fad6f4dcf822e25d01e4090e9a1
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e011add4e094d87ee10e84281e815a6a85454b0
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


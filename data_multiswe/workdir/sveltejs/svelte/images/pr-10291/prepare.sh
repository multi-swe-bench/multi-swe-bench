#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 107ec1c848e0d3494a2d798c8c088a93752a392a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true


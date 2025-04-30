#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout ffd0473e0f56de0f0d16b05b85d6b6f2e46bf10e
bash /home/check_git_changes.sh

pnpm install || true


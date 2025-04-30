#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 68e5cc6ac8fc289372831c5fbdff09e63728fc00
bash /home/check_git_changes.sh

pnpm install || true


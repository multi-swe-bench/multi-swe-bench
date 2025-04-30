#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout edf2572615d0b065bb7ae49de4c3b71086771310
bash /home/check_git_changes.sh

pnpm install || true


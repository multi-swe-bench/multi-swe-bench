#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 1c3327a0fa5983aa9078e3f7bb2330f572435425
bash /home/check_git_changes.sh

pnpm install || true


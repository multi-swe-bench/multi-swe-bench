#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 6277cb994acecf56f5f0745f5e2dac9785a34957
bash /home/check_git_changes.sh

pnpm install || true


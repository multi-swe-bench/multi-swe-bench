#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 314ce82e479dbb33a9281ba8c2ebe288536b32df
bash /home/check_git_changes.sh

pnpm install || true


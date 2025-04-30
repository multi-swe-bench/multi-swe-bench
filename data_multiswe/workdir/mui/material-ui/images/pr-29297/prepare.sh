#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 2aa74087777bc3a7213c25b1f55836c43b3b3492
bash /home/check_git_changes.sh

yarn install || true


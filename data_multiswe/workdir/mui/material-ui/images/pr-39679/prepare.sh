#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b6f2e488d639e42d4e2d0518a0fecc4df5167c18
bash /home/check_git_changes.sh

yarn install || true


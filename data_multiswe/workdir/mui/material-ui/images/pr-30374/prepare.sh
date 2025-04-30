#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f22b27378ee98df1d8b300b1f6d639cdbb2c4929
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f22e9951931ecf68e8bce1c159d8e0384d92760c
bash /home/check_git_changes.sh

yarn install || true


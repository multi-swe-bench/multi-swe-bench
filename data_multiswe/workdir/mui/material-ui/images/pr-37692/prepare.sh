#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1af04d2aa1dd2356a24c7f31d7a2f7a174ba3cbb
bash /home/check_git_changes.sh

yarn install || true


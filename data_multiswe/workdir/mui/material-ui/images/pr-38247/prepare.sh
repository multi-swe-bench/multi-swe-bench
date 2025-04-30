#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 85c3c776918e43c8034d0fbdb1a35ded54c6b92d
bash /home/check_git_changes.sh

yarn install || true


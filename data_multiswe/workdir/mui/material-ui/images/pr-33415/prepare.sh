#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout dcb9db30a14bb64453c0278bfb9a35263702e2d2
bash /home/check_git_changes.sh

yarn install || true


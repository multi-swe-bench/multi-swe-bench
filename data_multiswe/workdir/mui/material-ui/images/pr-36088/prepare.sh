#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b1d2e8d375be4f2a238fe7bce81ad2bf5cb68ad1
bash /home/check_git_changes.sh

yarn install || true


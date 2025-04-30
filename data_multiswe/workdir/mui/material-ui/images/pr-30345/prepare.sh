#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 7767fb8f46abbe56f652bc59ed9637a8a1af9634
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 552f04e24d617a7b1d5cd83eaf14e8c19395ac24
bash /home/check_git_changes.sh

yarn install || true


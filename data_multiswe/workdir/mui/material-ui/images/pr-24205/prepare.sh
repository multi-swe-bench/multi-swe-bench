#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout dbaac3f35a31d2fc6f0ec3feb6c4125f5ec359b2
bash /home/check_git_changes.sh

yarn install || true


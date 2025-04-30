#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 194670d1cab86a764398648f136949a003b0c8b0
bash /home/check_git_changes.sh

yarn install || true


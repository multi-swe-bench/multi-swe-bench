#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 9f7a2bfac55faed1b1c6c7b4b6d1b1659a076bab
bash /home/check_git_changes.sh

yarn install || true


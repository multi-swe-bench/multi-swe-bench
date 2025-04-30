#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 375358b6f7d00342ad2a282c34950ebfb4b2cdc8
bash /home/check_git_changes.sh

yarn install || true


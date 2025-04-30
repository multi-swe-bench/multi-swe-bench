#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 30484b8d93b8255a2617d7af134653f4d29bcd4b
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 93b0aba905b3b6947f58a02d911489bb737ee880
bash /home/check_git_changes.sh

yarn install || true


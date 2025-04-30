#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 2991f58b34601595e5907a597deacdf753ab35f1
bash /home/check_git_changes.sh

yarn install || true


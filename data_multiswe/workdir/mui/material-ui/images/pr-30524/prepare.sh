#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout bbedbf79e07c32613ddcafee651ac3d501a82ff0
bash /home/check_git_changes.sh

yarn install || true


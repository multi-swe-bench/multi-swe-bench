#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 412f98170ddfa5e3d38980095142ba59214507f6
bash /home/check_git_changes.sh

yarn install || true


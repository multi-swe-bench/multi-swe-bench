#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 21b4e266d576a450b36a406ffada2dfb1f3d0192
bash /home/check_git_changes.sh

yarn install || true


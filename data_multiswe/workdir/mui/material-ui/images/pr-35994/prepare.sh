#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 2694045ca3d1273cfa1a3415c6ce4b971b298f7a
bash /home/check_git_changes.sh

yarn install || true


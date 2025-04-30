#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 04c0dd052dbb88b1eaf5ccb07c6f2ba57d63a662
bash /home/check_git_changes.sh

yarn install || true


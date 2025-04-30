#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout aac3631f8fdf5a404dff6d71365fd509f70fa847
bash /home/check_git_changes.sh

yarn install || true


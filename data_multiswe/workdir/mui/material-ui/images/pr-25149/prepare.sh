#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout fca2ddf44ce5518b82a464cfa806e30f1f973e5c
bash /home/check_git_changes.sh

yarn install || true


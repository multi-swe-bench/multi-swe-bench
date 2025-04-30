#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0d94283959a3aa016881b9644767b937c34d2807
bash /home/check_git_changes.sh

yarn install || true


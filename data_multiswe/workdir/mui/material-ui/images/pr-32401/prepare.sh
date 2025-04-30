#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 88db09044175734bb9f5e0fac2868e7a3ea6d485
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 5b6e6c5ccf19ffbf251cd19ead587774f17f6ec0
bash /home/check_git_changes.sh

yarn install || true


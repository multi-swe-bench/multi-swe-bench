#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 3e66b977cbadc8e688a6041b774db9695c34b654
bash /home/check_git_changes.sh

yarn install || true


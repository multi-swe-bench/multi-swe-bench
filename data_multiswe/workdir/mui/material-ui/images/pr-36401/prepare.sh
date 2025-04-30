#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b1b9ef7fae31cd34e3dc0be72439975f4a8bad6a
bash /home/check_git_changes.sh

yarn install || true


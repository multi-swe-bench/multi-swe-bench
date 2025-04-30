#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f403c091384cee51c6f4761180666985b5e34c4
bash /home/check_git_changes.sh

yarn install || true


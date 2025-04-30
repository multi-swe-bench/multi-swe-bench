#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e4618dc8abd01a9214a2b6faafdadae3d5f54d20
bash /home/check_git_changes.sh

yarn install || true


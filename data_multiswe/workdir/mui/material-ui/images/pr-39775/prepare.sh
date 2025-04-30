#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b9cee5d523304e0a8f3c8fd93a380d27be1df76
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout be6b6e2bc479473853ea2ecd367cd1a46c728ad9
bash /home/check_git_changes.sh

yarn install || true


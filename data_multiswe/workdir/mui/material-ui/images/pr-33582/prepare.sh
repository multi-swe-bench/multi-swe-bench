#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b2e1f01ef7d2433c92829dffd30e4ba484bd3d4f
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 75404f9ff09965be1bd7c9ed27154fd7536edde1
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b144a55f0ff8c2d45db00698fff2b0a077d2e619
bash /home/check_git_changes.sh

yarn install || true


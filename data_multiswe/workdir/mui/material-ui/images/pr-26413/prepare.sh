#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 2ec75363c13a6646499df0516a94d808e57f354b
bash /home/check_git_changes.sh

yarn install || true


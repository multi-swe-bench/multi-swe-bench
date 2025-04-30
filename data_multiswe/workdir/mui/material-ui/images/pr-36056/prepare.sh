#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1dc2782ddd66e3642ffc2175015d0af6de494a52
bash /home/check_git_changes.sh

yarn install || true


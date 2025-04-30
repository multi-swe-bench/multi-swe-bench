#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 22491f2568a93f49cfc20dae6a9a8b2cad4da957
bash /home/check_git_changes.sh

yarn install || true


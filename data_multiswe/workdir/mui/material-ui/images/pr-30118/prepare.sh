#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1dce3aadadfe4956bd0f265f816740d0a5d2b4b0
bash /home/check_git_changes.sh

yarn install || true


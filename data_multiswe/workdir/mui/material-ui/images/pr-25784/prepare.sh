#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b3c85de69ddf15a4a2e21b78b13e4c066b94ca2d
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c676e736337b914d7dc16f465212c47d7f2d50aa
bash /home/check_git_changes.sh

yarn install || true


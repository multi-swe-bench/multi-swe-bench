#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 812876d87be3ceeed0122b60e7003518b8ac6ea2
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 5047813ad0927fc040eca65d484ef4d6a8c8e9ec
bash /home/check_git_changes.sh

yarn install || true


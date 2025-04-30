#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout bca4565b43b4166f422aa4ba5d8399bb054bef66
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1104097f7c640cbe5db05465fcd104e3de6137d9
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b00bdc767032fd008e5e3ec3133d6dc51264b1de
bash /home/check_git_changes.sh

yarn install || true


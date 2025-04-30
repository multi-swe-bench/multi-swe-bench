#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 2890881a35de8bd364ccc7cab4fb7c2c227b130f
bash /home/check_git_changes.sh

yarn install || true


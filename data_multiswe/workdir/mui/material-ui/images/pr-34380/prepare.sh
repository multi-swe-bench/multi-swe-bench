#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1350aa87e9310059a15b5f3b6032775b61d62060
bash /home/check_git_changes.sh

yarn install || true


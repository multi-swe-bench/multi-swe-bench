#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 641132490fdc09dd4530e9de6859d504100fc52a
bash /home/check_git_changes.sh

yarn install || true


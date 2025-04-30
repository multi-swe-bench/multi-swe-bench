#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a4d8c4ffadca14ebb941003082e607a96eacb409
bash /home/check_git_changes.sh

yarn install || true


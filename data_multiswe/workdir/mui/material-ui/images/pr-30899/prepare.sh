#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 171942ce6e9f242900928620610a794daf8e559c
bash /home/check_git_changes.sh

yarn install || true


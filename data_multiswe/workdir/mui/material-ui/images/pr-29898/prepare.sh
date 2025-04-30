#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 38ac830eedf60a2a40983d71cb4dd64e8f1abf4e
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout dba967d2e24475711b5fe870bc9d8083a1485252
bash /home/check_git_changes.sh

yarn install || true


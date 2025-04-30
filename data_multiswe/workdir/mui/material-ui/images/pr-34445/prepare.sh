#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 82d5d37106179635e7ed9c0efd962139ff62b5ea
bash /home/check_git_changes.sh

yarn install || true


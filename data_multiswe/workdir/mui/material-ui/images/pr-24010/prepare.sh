#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 3506dda5d69fc237e8f241370c7fdf4d8a105370
bash /home/check_git_changes.sh

yarn install || true


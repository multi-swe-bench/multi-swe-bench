#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 4c44bedf531708518db2d9b0d9a42b379108fb5a
bash /home/check_git_changes.sh

yarn install || true


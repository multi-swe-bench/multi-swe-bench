#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout cfdaf61447bededf654bb1fd76332c8dea8784e3
bash /home/check_git_changes.sh

yarn install || true


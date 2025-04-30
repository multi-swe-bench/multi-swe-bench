#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 17695ff6be0aa6c7e4c81cadee5b9c8fb0c1a0b8
bash /home/check_git_changes.sh

yarn install || true


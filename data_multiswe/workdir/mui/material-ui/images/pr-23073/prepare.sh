#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 754e29cf5a712d0e0f6bd3e54f80e9997659f68c
bash /home/check_git_changes.sh

yarn install || true


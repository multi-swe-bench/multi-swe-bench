#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 9710ff34b16a0f271107a8619a28546ae3ca7c18
bash /home/check_git_changes.sh

yarn install || true


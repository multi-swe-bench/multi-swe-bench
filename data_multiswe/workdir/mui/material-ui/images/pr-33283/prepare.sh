#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 72e64c6c363e9f4f9faf7808e72527e584024549
bash /home/check_git_changes.sh

yarn install || true


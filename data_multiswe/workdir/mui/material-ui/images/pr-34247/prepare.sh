#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6006aa39784a81fdfa0eb96bd2001b3eb86bd829
bash /home/check_git_changes.sh

yarn install || true


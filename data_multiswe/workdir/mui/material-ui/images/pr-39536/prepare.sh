#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c577e38f0711a6105e8b819c4549963a77e4ef08
bash /home/check_git_changes.sh

yarn install || true


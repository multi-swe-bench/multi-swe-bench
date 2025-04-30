#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 553cf822f6500075d374f3e89ad04b8308cd9f47
bash /home/check_git_changes.sh

yarn install || true


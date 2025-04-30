#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c3fc8b881aee6c0ca85718550e7d60a4c2b9d1c1
bash /home/check_git_changes.sh

yarn install || true


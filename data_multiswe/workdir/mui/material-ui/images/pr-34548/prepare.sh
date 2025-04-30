#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 139724acb3ff53e7f4c8a3a3be90d004f8b8309f
bash /home/check_git_changes.sh

yarn install || true


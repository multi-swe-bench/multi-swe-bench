#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6d732baac5eee9027a7cb4a7be9d165b8c705936
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 36c1e08520f8add7bdc341825d44f50d59ceab83
bash /home/check_git_changes.sh

yarn install || true


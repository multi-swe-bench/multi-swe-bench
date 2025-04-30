#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 43408b10ef81ff885c3ad69bd1c9df21680960d4
bash /home/check_git_changes.sh

yarn install || true


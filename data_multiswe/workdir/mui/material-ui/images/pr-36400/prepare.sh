#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e05f16c4c5070a69abaa143d513a1f831f8dbfb9
bash /home/check_git_changes.sh

yarn install || true


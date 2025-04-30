#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a731e863cb13c83f4d6b9b4c7dd3633fad8f1ed4
bash /home/check_git_changes.sh

yarn install || true


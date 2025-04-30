#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0ba283880545390fc6408e408dcde93ed5de178c
bash /home/check_git_changes.sh

yarn install || true


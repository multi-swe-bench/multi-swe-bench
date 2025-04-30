#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e242809731743f195b4ea6477cfe95e96ea00b8e
bash /home/check_git_changes.sh

yarn install || true


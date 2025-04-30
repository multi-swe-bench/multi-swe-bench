#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 7e7435ad08ba02a0e1d8d8676a519b8ded634149
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a96f9ca2297c1293cf1c5b96cb0de255d2f4a8a
bash /home/check_git_changes.sh

yarn install || true


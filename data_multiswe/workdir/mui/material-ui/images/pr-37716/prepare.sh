#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 05917392afce8bcd80b290749e5ecd879768d6fe
bash /home/check_git_changes.sh

yarn install || true


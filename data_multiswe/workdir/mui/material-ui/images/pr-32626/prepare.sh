#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 414c2ad63dd766587ca1ae786fdf0b879976a242
bash /home/check_git_changes.sh

yarn install || true


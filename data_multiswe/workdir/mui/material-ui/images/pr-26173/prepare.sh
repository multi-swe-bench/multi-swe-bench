#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 205258b56faf4ac8096d10b62e22458dab52fb8e
bash /home/check_git_changes.sh

yarn install || true


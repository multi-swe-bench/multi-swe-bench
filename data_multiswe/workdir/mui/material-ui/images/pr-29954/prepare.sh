#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 145a5ecbfce78ebe5c94a19417da82da01d1b28a
bash /home/check_git_changes.sh

yarn install || true


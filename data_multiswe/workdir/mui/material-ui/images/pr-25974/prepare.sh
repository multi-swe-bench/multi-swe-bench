#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a030b0e07e1354790790d9be1baa227044ce2d50
bash /home/check_git_changes.sh

yarn install || true


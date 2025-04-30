#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b6cdaaf1a7f60de9ed66a491b7477fad19429905
bash /home/check_git_changes.sh

yarn install || true


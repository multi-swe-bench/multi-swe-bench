#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ef7d1cbfbbb03e27addf356f0e7d57033b4ef0b
bash /home/check_git_changes.sh

yarn install || true


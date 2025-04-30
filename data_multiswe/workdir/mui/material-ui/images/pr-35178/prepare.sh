#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1ea442da69a48694c3880e1302cfc10eb85e93eb
bash /home/check_git_changes.sh

yarn install || true


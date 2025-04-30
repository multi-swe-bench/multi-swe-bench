#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d7c0ae5958a274c6d7043b3bda8291a1d93fd3c1
bash /home/check_git_changes.sh

yarn install || true


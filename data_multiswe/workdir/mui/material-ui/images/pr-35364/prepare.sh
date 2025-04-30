#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 9e140a77ebd8464e2b400b1d1d19fc63c387a864
bash /home/check_git_changes.sh

yarn install || true


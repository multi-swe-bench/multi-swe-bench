#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a11ad3d74a95961c9660c0f50bd2dac1d0204c60
bash /home/check_git_changes.sh

yarn install || true


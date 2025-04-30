#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 7cb56d2cef3f4e5e4f39214661da951c26eba9da
bash /home/check_git_changes.sh

yarn install || true


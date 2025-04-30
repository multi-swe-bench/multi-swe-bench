#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 215794b567669951a61183d748c0b2be6483c3ea
bash /home/check_git_changes.sh

yarn install || true


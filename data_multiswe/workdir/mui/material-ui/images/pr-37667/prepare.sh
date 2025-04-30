#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0c627118be280cd91ffae0bed7ccc786617c6773
bash /home/check_git_changes.sh

yarn install || true


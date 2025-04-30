#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 43a929dda5a0776bcc05f4624a5648441d44c7b2
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0198612f091c8d52310717106f234c81199d4d35
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f56be2a07185be06984476aed9f518cbbd6b87d
bash /home/check_git_changes.sh

yarn install || true


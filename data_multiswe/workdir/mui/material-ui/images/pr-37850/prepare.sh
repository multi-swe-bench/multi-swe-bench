#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout eb8e95bacf06f824f9e88e7cf1399be1fa23b48f
bash /home/check_git_changes.sh

yarn install || true


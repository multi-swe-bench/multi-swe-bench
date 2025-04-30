#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 58504fa3345fbd2c70c59f7ce2e9d634afe01e38
bash /home/check_git_changes.sh

yarn install || true


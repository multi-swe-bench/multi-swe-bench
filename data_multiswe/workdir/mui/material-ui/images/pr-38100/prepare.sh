#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0f8eb07edbf21c585faf4803ab0122f23efbb2c7
bash /home/check_git_changes.sh

yarn install || true


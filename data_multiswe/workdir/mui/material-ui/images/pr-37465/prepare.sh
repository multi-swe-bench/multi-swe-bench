#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout bf1a4fc8f9fba7dad9657ce6db1d5500b8aaf4cf
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e9b324c880892e9c6ebd2a627f0311478f50252b
bash /home/check_git_changes.sh

yarn install || true


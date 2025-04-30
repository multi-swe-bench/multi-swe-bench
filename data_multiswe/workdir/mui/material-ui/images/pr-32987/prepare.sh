#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 67186bfbce12163569f9e5a9c94d7ff2dd33f6fd
bash /home/check_git_changes.sh

yarn install || true


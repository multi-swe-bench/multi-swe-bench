#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 22b7f0c0a0d3a87113a34a85c27ccb8053e02487
bash /home/check_git_changes.sh

yarn install || true


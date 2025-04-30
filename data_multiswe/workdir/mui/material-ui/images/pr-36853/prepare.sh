#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 44748d4c1f5272f00bb362af2869895ce8c28677
bash /home/check_git_changes.sh

yarn install || true


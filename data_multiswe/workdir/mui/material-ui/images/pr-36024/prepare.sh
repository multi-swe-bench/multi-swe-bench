#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 910d3a4ca46c6f79b7b5507c35532774c38460d2
bash /home/check_git_changes.sh

yarn install || true


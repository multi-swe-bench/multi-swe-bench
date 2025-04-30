#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 89c820ac86ca54d6d8b25309f9b43803e68903dc
bash /home/check_git_changes.sh

yarn install || true


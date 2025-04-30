#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c3aab53e78396e944a6e36348057a9f0df3ec762
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d05dfcf2a8602874052e9fe9f79566afad05956f
bash /home/check_git_changes.sh

yarn install || true


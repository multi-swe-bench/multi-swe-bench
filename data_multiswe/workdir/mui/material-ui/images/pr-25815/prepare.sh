#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a14696593902fd422b8f759d45b1b7ee409223f1
bash /home/check_git_changes.sh

yarn install || true


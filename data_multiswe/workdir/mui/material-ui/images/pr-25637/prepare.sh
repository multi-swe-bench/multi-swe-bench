#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d2e00769d0322dc911dd6237e30ab592aa02cad9
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 71a18fb6a9252e2200a0d576e66d55fbd81b85bd
bash /home/check_git_changes.sh

yarn install || true


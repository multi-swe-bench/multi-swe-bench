#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0486f4b2952519d9a01c17dc45841523acdd7f92
bash /home/check_git_changes.sh

yarn install || true


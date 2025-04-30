#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout ea2bd5aa822dfd4e46a0cdf3d68f90f7f2e6d757
bash /home/check_git_changes.sh

yarn install || true


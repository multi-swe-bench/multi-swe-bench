#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 91ad7e8afe2b43b61815c31830f8b1a553fc9e91
bash /home/check_git_changes.sh

yarn install || true


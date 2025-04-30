#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 8a86d1e375943d33ddb4a19f272e8432ba1fa5c3
bash /home/check_git_changes.sh

yarn install || true


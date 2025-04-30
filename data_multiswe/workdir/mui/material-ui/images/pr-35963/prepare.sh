#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout dbddc26ff0e421603a196e68e4d80878d262c632
bash /home/check_git_changes.sh

yarn install || true


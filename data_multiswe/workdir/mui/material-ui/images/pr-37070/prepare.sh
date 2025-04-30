#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout fe90fe90b28bf357bec47eaf9641d6bc3a862bd1
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b3548fabeab1980d3c5e5b85945550df95ee6b82
bash /home/check_git_changes.sh

yarn install || true


#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout fe7ac373c763867a0eb1eb5be8da09b303d9e417
bash /home/check_git_changes.sh

yarn install || true

